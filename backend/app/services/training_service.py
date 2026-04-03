"""
模型训练服务
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.models.database import TrainingJob, TrainingDataset, Prediction
from app.core.database import SessionLocal
from datetime import datetime
import threading
import json

# 训练任务字典，用于跟踪和取消训练
training_threads = {}


class HistoryDataset(Dataset):
    """从识别历史创建的数据集"""

    def __init__(self, predictions, transform=None):
        self.predictions = predictions
        self.transform = transform

        # 创建类别到索引的映射
        self.classes = sorted(list(set(p.predicted_class for p in predictions)))
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}

    def __len__(self):
        return len(self.predictions)

    def __getitem__(self, idx):
        pred = self.predictions[idx]

        # 加载图片
        try:
            image = Image.open(pred.image_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
        except Exception as e:
            # 如果图片加载失败，返回黑色图片
            image = torch.zeros(3, 224, 224)

        label = self.class_to_idx[pred.predicted_class]
        return image, label


def prepare_dataset(dataset_id: int, db: Session):
    """准备训练数据集"""
    dataset = db.query(TrainingDataset).filter(TrainingDataset.id == dataset_id).first()
    if not dataset:
        raise ValueError("数据集不存在")

    if dataset.source_type == "history":
        # 从识别历史加载数据
        predictions = db.query(Prediction).filter(Prediction.predicted_class.isnot(None)).all()

        # 数据增强
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        return HistoryDataset(predictions, transform=transform)
    else:
        raise NotImplementedError("暂不支持上传数据集")


def train_model(job_id: int):
    """训练模型（在后台线程中运行）"""
    db = SessionLocal()

    try:
        # 获取训练任务
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if not job:
            return

        # 更新状态为运行中
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        # 准备数据集
        dataset = prepare_dataset(job.dataset_id, db)
        train_loader = DataLoader(dataset, batch_size=job.training_params.get('batch_size', 32), shuffle=True)

        # 初始化模型（使用MobileNetV2）
        model = models.mobilenet_v2(pretrained=True)
        num_classes = len(dataset.classes)
        model.classifier[1] = nn.Linear(model.last_channel, num_classes)

        # 设置设备
        device = torch.device('cpu')  # 用户要求不使用GPU
        model = model.to(device)

        # 损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=job.training_params.get('learning_rate', 0.001))

        # 训练循环
        total_epochs = job.training_params.get('epochs', 10)

        for epoch in range(total_epochs):
            # 检查是否被取消
            db.refresh(job)
            if job.status == "cancelled":
                break

            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            for batch_idx, (inputs, labels) in enumerate(train_loader):
                inputs, labels = inputs.to(device), labels.to(device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

            # 计算指标
            epoch_loss = running_loss / len(train_loader)
            epoch_acc = 100. * correct / total

            # 更新进度
            job.current_epoch = epoch + 1
            job.progress = (epoch + 1) / total_epochs * 100
            job.loss = epoch_loss
            job.accuracy = epoch_acc
            db.commit()

        # 训练完成，保存模型
        if job.status != "cancelled":
            model_dir = "ml_models"
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{job.name}.pth")

            # 保存模型和类别映射
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': dataset.classes,
                'class_to_idx': dataset.class_to_idx
            }, model_path)

            job.model_path = model_path
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()

    except Exception as e:
        # 训练失败
        job.status = "failed"
        job.completed_at = datetime.utcnow()
        db.commit()
        print(f"训练失败: {str(e)}")

    finally:
        db.close()
        # 从线程字典中移除
        if job_id in training_threads:
            del training_threads[job_id]


def start_training(job_id: int):
    """启动训练任务"""
    if job_id in training_threads:
        raise ValueError("训练任务已在运行中")

    # 创建并启动训练线程
    thread = threading.Thread(target=train_model, args=(job_id,))
    thread.daemon = True
    thread.start()

    training_threads[job_id] = thread
