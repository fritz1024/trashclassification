"""
AI聊天API路由
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.core.logger import logger

router = APIRouter(prefix="/api/chat", tags=["AI聊天"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI聊天接口

    支持多轮对话，前端需要传递完整的对话历史
    """
    try:
        # 将Pydantic模型转换为字典列表
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        logger.info(f"收到聊天请求，消息数量: {len(messages)}")

        # 调用AI服务
        reply = ai_service.chat(messages)

        return ChatResponse(
            reply=reply,
            success=True
        )

    except Exception as e:
        logger.error(f"聊天接口异常: {str(e)}", exc_info=True)
        return ChatResponse(
            reply="抱歉，服务暂时不可用，请稍后再试。",
            success=False,
            error=str(e)
        )


@router.get("/health")
async def health_check():
    """
    检查AI服务是否可用
    """
    from app.core.config import settings

    if settings.DASHSCOPE_API_KEY:
        return {
            "status": "ok",
            "message": "AI聊天服务已配置"
        }
    else:
        return {
            "status": "unavailable",
            "message": "AI聊天服务未配置 API Key"
        }
