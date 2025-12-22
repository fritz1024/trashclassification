"""
模型推理服务
"""
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
from typing import List, Tuple
from app.core.config import settings


class ModelService:
    """模型推理服务类"""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = None
        self.class_names = None
        self._load_model()
        self._setup_transform()
        self._load_class_names()

    def _load_model(self):
        """加载模型"""
        print(f"加载模型: {settings.MODEL_PATH}")

        # 创建模型结构
        model = models.mobilenet_v2(pretrained=False)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, settings.NUM_CLASSES)

        # 加载权重
        checkpoint = torch.load(settings.MODEL_PATH, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])

        model = model.to(self.device)
        model.eval()

        self.model = model
        print(f"模型加载成功，使用设备: {self.device}")

    def _setup_transform(self):
        """设置图像预处理"""
        self.transform = transforms.Compose([
            transforms.Resize((settings.IMG_SIZE, settings.IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _load_class_names(self):
        """加载类别名称映射"""
        class_names_file = os.path.join(os.path.dirname(__file__), '../../ml_models/classname.txt')

        # 如果文件不存在，尝试从项目根目录加载
        if not os.path.exists(class_names_file):
            class_names_file = os.path.join(os.path.dirname(__file__), '../../../classname.txt')

        if os.path.exists(class_names_file):
            try:
                with open(class_names_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 类别ID从0开始，对应文件的第1行
                    self.class_names = {i: line.strip() for i, line in enumerate(lines)}
                print(f"成功加载 {len(self.class_names)} 个类别名称")
            except Exception as e:
                print(f"加载类别名称失败: {str(e)}")
                # 使用默认名称
                self.class_names = {i: f"垃圾类别_{i}" for i in range(settings.NUM_CLASSES)}
        else:
            print(f"类别名称文件不存在: {class_names_file}")
            # 使用默认名称
            self.class_names = {i: f"垃圾类别_{i}" for i in range(settings.NUM_CLASSES)}

    def predict(self, image_path: str) -> Tuple[int, float, List[dict]]:
        """
        预测单张图片

        Args:
            image_path: 图片路径

        Returns:
            (predicted_class_id, confidence, top3_results)
        """
        # 加载图片
        image = Image.open(image_path).convert('RGB')

        # 预处理
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 推理
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)

        # 获取Top-3结果
        top3_prob, top3_idx = torch.topk(probabilities, 3)

        top3_results = []
        for i in range(3):
            class_id = top3_idx[0][i].item()
            confidence = top3_prob[0][i].item()
            class_name = self.class_names.get(class_id, f"类别_{class_id}")

            top3_results.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(confidence * 100, 2)
            })

        # 返回最高置信度的结果
        predicted_class_id = top3_results[0]["class_id"]
        predicted_confidence = top3_results[0]["confidence"]

        return predicted_class_id, predicted_confidence, top3_results

    def get_class_name(self, class_id: int) -> str:
        """获取类别名称"""
        return self.class_names.get(class_id, f"类别_{class_id}")


# 全局模型服务实例
model_service = ModelService()
