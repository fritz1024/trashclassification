"""
FastAPI主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings as config_settings
from app.core.database import engine
from app.core.logger import logger
from app.models.database import Base
from app.api import auth, predict, stats, admin, chat, reports, model, announcements, settings, knowledge, training
import os
import time

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=config_settings.APP_NAME,
    version=config_settings.APP_VERSION,
    description="基于MobileNetV2的智能垃圾分类识别系统"
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()

    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应信息
        logger.info(
            f"请求完成: {request.method} {request.url.path} "
            f"状态码={response.status_code} 耗时={process_time:.3f}s"
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"请求失败: {request.method} {request.url.path} "
            f"错误={str(e)} 耗时={process_time:.3f}s",
            exc_info=True
        )
        raise

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在
os.makedirs(config_settings.UPLOAD_DIR, exist_ok=True)
logger.info(f"上传目录已创建: {config_settings.UPLOAD_DIR}")

# 挂载静态文件目录（用于访问上传的图片）
app.mount("/uploads", StaticFiles(directory=config_settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(stats.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(model.router)
app.include_router(announcements.router)
app.include_router(settings.router)
app.include_router(knowledge.router)
app.include_router(training.router)
logger.info("所有路由已注册")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 50)
    logger.info(f"{config_settings.APP_NAME} v{config_settings.APP_VERSION} 启动中...")
    logger.info(f"调试模式: {config_settings.DEBUG}")
    logger.info(f"数据库: {config_settings.DATABASE_URL}")
    logger.info(f"模型路径: {config_settings.MODEL_PATH}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("=" * 50)
    logger.info(f"{config_settings.APP_NAME} 正在关闭...")
    logger.info("=" * 50)


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用垃圾分类识别系统API",
        "version": config_settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    logger.info("使用 uvicorn 启动应用...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
