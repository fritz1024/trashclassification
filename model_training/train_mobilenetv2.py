"""
使用 MobileNetV2 进行垃圾分类模型训练
适用于阿里云GPU服务器
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from PIL import Image
import pandas as pd
import os
from tqdm import tqdm

# ==================== 配置区域 ====================
DATA_DIR = "./data"
BATCH_SIZE = 128              # 优化：从32提升到128，充分利用A10的24GB显存
NUM_EPOCHS = 50
LEARNING_RATE = 0.001
NUM_CLASSES = 265
IMG_SIZE = 224
NUM_WORKERS = 8               # 优化：从4提升到8，匹配8核CPU

# ==================== 数据集类 ====================
class GarbageDataset(Dataset):
    """垃圾分类数据集"""

    def __init__(self, csv_file, data_dir, transform=None):
        """
        Args:
            csv_file: CSV标注文件路径
            data_dir: 数据根目录
            transform: 数据增强
        """
        self.data = pd.read_csv(csv_file)
        self.data_dir = data_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = os.path.join(self.data_dir, self.data.iloc[idx, 0])
        image = Image.open(img_path).convert('RGB')
        label = int(self.data.iloc[idx, 1])

        if self.transform:
            image = self.transform(image)

        return image, label

# ==================== 数据增强 ====================
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# ==================== 模型定义 ====================
def create_model(num_classes=265, pretrained=True):
    """创建 MobileNetV2 模型"""
    model = models.mobilenet_v2(pretrained=pretrained)

    # 修改最后的分类层
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)

    return model

# ==================== 训练函数 ====================
def train_epoch(model, dataloader, criterion, optimizer, device):
    """训练一个epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc='Training')
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        pbar.set_postfix({
            'loss': f'{running_loss/len(dataloader):.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })

    return running_loss / len(dataloader), 100. * correct / total

# ==================== 验证函数 ====================
def validate(model, dataloader, criterion, device):
    """验证模型"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        pbar = tqdm(dataloader, desc='Validation')
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            pbar.set_postfix({
                'loss': f'{running_loss/len(dataloader):.4f}',
                'acc': f'{100.*correct/total:.2f}%'
            })

    return running_loss / len(dataloader), 100. * correct / total

# ==================== 主训练流程 ====================
def main():
    print("=" * 60)
    print("垃圾分类 MobileNetV2 训练")
    print("=" * 60)

    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

    # 加载数据集
    print("\n加载数据集...")
    train_dataset = GarbageDataset(
        csv_file=os.path.join(DATA_DIR, 'train.csv'),
        data_dir=DATA_DIR,
        transform=train_transform
    )

    val_dataset = GarbageDataset(
        csv_file=os.path.join(DATA_DIR, 'val.csv'),
        data_dir=DATA_DIR,
        transform=val_transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    print(f"训练集大小: {len(train_dataset)}")
    print(f"验证集大小: {len(val_dataset)}")
    print(f"类别数量: {NUM_CLASSES}")

    # 创建模型
    print("\n创建 MobileNetV2 模型...")
    model = create_model(num_classes=NUM_CLASSES, pretrained=True)
    model = model.to(device)

    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=True
    )

    # 训练循环
    print("\n开始训练...")
    print("=" * 60)

    best_acc = 0.0

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")
        print("-" * 60)

        # 训练
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device
        )

        # 验证
        val_loss, val_acc = validate(
            model, val_loader, criterion, device
        )

        # 学习率调整
        scheduler.step(val_acc)

        print(f"\nEpoch {epoch+1} 结果:")
        print(f"  训练 - Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
        print(f"  验证 - Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")

        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_acc': best_acc,
            }, 'best_model.pth')
            print(f"  ✓ 保存最佳模型 (验证准确率: {best_acc:.2f}%)")

        # 定期保存检查点
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_acc': best_acc,
            }, f'checkpoint_epoch_{epoch+1}.pth')

    print("\n" + "=" * 60)
    print(f"训练完成！最佳验证准确率: {best_acc:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
