"""
模型管理相关API路由
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.database import Prediction, Feedback
from app.api.auth import require_admin
from datetime import datetime, timedelta
import os
import shutil
import json

router = APIRouter(prefix="/api/model", tags=["模型管理"])

# 获取backend目录路径
def get_backend_dir():
    """获取backend目录的绝对路径"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 获取模型目录路径
def get_models_dir():
    """获取models目录的绝对路径"""
    backend_dir = get_backend_dir()
    models_dir = os.path.join(backend_dir, "ml_models")
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

# 获取当前使用的模型配置
def get_current_model_config():
    """读取当前使用的模型配置"""
    backend_dir = get_backend_dir()
    config_path = os.path.join(backend_dir, "current_model.json")

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 默认配置
        return {"model_file": "best_model.pth"}

# 设置当前使用的模型
def set_current_model_config(model_file):
    """保存当前使用的模型配置"""
    backend_dir = get_backend_dir()
    config_path = os.path.join(backend_dir, "current_model.json")

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({"model_file": model_file}, f, ensure_ascii=False, indent=2)

@router.get("/list")
def get_model_list(admin_user = Depends(require_admin)):
    """获取所有可用的模型列表"""
    backend_dir = get_backend_dir()
    models_dir = get_models_dir()
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")
    
    models = []
    
    # 扫描backend目录和models目录下的.pth文件
    for directory in [backend_dir, models_dir]:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.pth'):
                    file_path = os.path.join(directory, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    timestamp = os.path.getmtime(file_path)
                    updated_at = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    
                    models.append({
                        "name": file,
                        "size_mb": round(file_size, 2),
                        "updated_at": updated_at,
                        "is_current": file == current_model,
                        "path": file_path
                    })
    
    # 按更新时间倒序排序
    models.sort(key=lambda x: x["updated_at"], reverse=True)
    
    return {
        "total": len(models),
        "current_model": current_model,
        "models": models
    }

@router.post("/upload")
async def upload_model(
    file: UploadFile = File(...),
    admin_user = Depends(require_admin)
):
    """上传新模型文件"""
    # 检查文件扩展名
    if not file.filename.endswith('.pth'):
        raise HTTPException(status_code=400, detail="只支持.pth格式的模型文件")
    
    # 保存到models目录
    models_dir = get_models_dir()
    file_path = os.path.join(models_dir, file.filename)
    
    # 如果文件已存在，添加时间戳
    if os.path.exists(file_path):
        name, ext = os.path.splitext(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file.filename = f"{name}_{timestamp}{ext}"
        file_path = os.path.join(models_dir, file.filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    
    return {
        "message": "模型上传成功",
        "filename": file.filename,
        "size_mb": round(file_size, 2)
    }

@router.post("/switch")
def switch_model(
    model_name: str,
    admin_user = Depends(require_admin)
):
    """切换当前使用的模型"""
    backend_dir = get_backend_dir()
    models_dir = get_models_dir()
    
    # 检查模型文件是否存在
    model_path = None
    for directory in [backend_dir, models_dir]:
        potential_path = os.path.join(directory, model_name)
        if os.path.exists(potential_path):
            model_path = potential_path
            break
    
    if not model_path:
        raise HTTPException(status_code=404, detail="模型文件不存在")
    
    # 更新配置
    set_current_model_config(model_name)
    
    return {
        "message": "模型切换成功",
        "current_model": model_name
    }

@router.delete("/delete")
def delete_model(
    model_name: str,
    admin_user = Depends(require_admin)
):
    """删除模型文件"""
    backend_dir = get_backend_dir()
    models_dir = get_models_dir()
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")
    
    # 不允许删除当前正在使用的模型
    if model_name == current_model:
        raise HTTPException(status_code=400, detail="不能删除当前正在使用的模型")
    
    # 查找并删除模型文件
    model_path = None
    for directory in [backend_dir, models_dir]:
        potential_path = os.path.join(directory, model_name)
        if os.path.exists(potential_path):
            model_path = potential_path
            break
    
    if not model_path:
        raise HTTPException(status_code=404, detail="模型文件不存在")
    
    # 删除文件
    os.remove(model_path)
    
    return {
        "message": "模型删除成功",
        "deleted_model": model_name
    }

@router.get("/info")
def get_model_info(admin_user = Depends(require_admin)):
    """获取当前模型信息"""
    backend_dir = get_backend_dir()
    models_dir = get_models_dir()
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")
    
    # 查找当前模型文件
    model_path = None
    for directory in [backend_dir, models_dir]:
        potential_path = os.path.join(directory, current_model)
        if os.path.exists(potential_path):
            model_path = potential_path
            break
    
    model_exists = model_path is not None
    model_size = 0
    model_updated = None
    
    if model_exists:
        model_size = os.path.getsize(model_path) / (1024 * 1024)
        timestamp = os.path.getmtime(model_path)
        model_updated = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "model_name": "MobileNetV2",
        "model_file": current_model,
        "model_path": model_path,
        "model_exists": model_exists,
        "model_size_mb": round(model_size, 2),
        "model_updated": model_updated,
        "num_classes": 4,
        "categories": ["可回收物", "有害垃圾", "厨余垃圾", "其他垃圾"]
    }

@router.get("/performance")
def get_model_performance(
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """获取模型性能统计"""
    # 获取当前使用的模型名称
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")

    # 只统计当前模型的数据
    total_predictions = db.query(Prediction).filter(Prediction.model_name == current_model).count()
    avg_confidence = db.query(func.avg(Prediction.confidence)).filter(Prediction.model_name == current_model).scalar() or 0
    high_confidence_count = db.query(Prediction).filter(Prediction.model_name == current_model, Prediction.confidence >= 80).count()
    low_confidence_count = db.query(Prediction).filter(Prediction.model_name == current_model, Prediction.confidence < 60).count()

    category_distribution = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).filter(Prediction.model_name == current_model).group_by(Prediction.predicted_class).all()

    return {
        "total_predictions": total_predictions,
        "avg_confidence": round(avg_confidence, 2),
        "high_confidence_count": high_confidence_count,
        "low_confidence_count": low_confidence_count,
        "high_confidence_rate": round(high_confidence_count / total_predictions * 100, 2) if total_predictions > 0 else 0,
        "category_distribution": [
            {"category": cat, "count": count}
            for cat, count in category_distribution
        ]
    }

@router.get("/error-cases")
def get_error_cases(
    limit: int = 20,
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """获取错误识别案例（基于用户反馈）"""
    # 获取当前使用的模型名称
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")

    # 只查询当前模型的错误案例
    error_cases = db.query(
        Prediction.id,
        Prediction.image_path,
        Prediction.predicted_class,
        Prediction.confidence,
        Prediction.created_at,
        Feedback.correct_class,
        Feedback.comment
    ).join(
        Feedback, Prediction.id == Feedback.prediction_id
    ).filter(
        Prediction.predicted_class != Feedback.correct_class,
        Prediction.model_name == current_model
    ).order_by(
        desc(Prediction.created_at)
    ).limit(limit).all()
    
    items = []
    for index, case in enumerate(error_cases, start=1):
        items.append({
            "index": index,
            "image_path": case.image_path,
            "predicted_class": case.predicted_class,
            "correct_class": case.correct_class,
            "confidence": case.confidence,
            "comment": case.comment,
            "created_at": case.created_at
        })
    
    return {
        "total": len(items),
        "items": items
    }


@router.get("/compare")
def compare_models(
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """对比所有模型的性能"""
    # 获取所有使用过的模型名称
    model_names = db.query(Prediction.model_name).distinct().all()
    model_names = [name[0] for name in model_names if name[0]]
    
    comparison_data = []
    
    for model_name in model_names:
        # 统计每个模型的数据
        total = db.query(Prediction).filter(Prediction.model_name == model_name).count()
        avg_conf = db.query(func.avg(Prediction.confidence)).filter(Prediction.model_name == model_name).scalar() or 0
        high_conf = db.query(Prediction).filter(Prediction.model_name == model_name, Prediction.confidence >= 80).count()
        
        comparison_data.append({
            "model_name": model_name,
            "total_predictions": total,
            "avg_confidence": round(avg_conf, 2),
            "high_confidence_count": high_conf,
            "high_confidence_rate": round(high_conf / total * 100, 2) if total > 0 else 0
        })
    
    # 按总识别次数排序
    comparison_data.sort(key=lambda x: x["total_predictions"], reverse=True)
    
    return {
        "total_models": len(comparison_data),
        "models": comparison_data
    }


@router.get("/current")
def get_current_model():
    """获取当前使用的模型名称（公开接口）"""
    current_config = get_current_model_config()
    current_model = current_config.get("model_file", "best_model.pth")
    
    return {
        "model_file": current_model,
        "model_name": "MobileNetV2"
    }
