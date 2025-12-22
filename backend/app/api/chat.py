"""
AI聊天API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse
)
from app.services.ai_service import ai_service
from app.core.logger import logger
from app.core.database import get_db
from app.models.database import ChatConversation, User
from app.api.auth import get_current_user

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


# ==================== 对话历史管理 API ====================

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有对话历史
    """
    try:
        conversations = db.query(ChatConversation).filter(
            ChatConversation.user_id == current_user.id
        ).order_by(ChatConversation.updated_at.desc()).all()

        return conversations

    except Exception as e:
        logger.error(f"获取对话历史失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取对话历史失败")


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定对话的详情
    """
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取对话详情失败")


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新对话
    """
    try:
        # 将 Pydantic 模型转换为字典列表
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in conversation.messages]

        new_conversation = ChatConversation(
            user_id=current_user.id,
            title=conversation.title,
            messages=messages_dict
        )

        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        logger.info(f"用户 {current_user.username} 创建了新对话: {new_conversation.id}")

        return new_conversation

    except Exception as e:
        db.rollback()
        logger.error(f"创建对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建对话失败")


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新对话
    """
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")

        # 更新标题
        if conversation_update.title is not None:
            conversation.title = conversation_update.title

        # 更新消息
        if conversation_update.messages is not None:
            messages_dict = [{"role": msg.role, "content": msg.content} for msg in conversation_update.messages]
            conversation.messages = messages_dict

        db.commit()
        db.refresh(conversation)

        logger.info(f"用户 {current_user.username} 更新了对话: {conversation_id}")

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="更新对话失败")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除对话
    """
    try:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")

        db.delete(conversation)
        db.commit()

        logger.info(f"用户 {current_user.username} 删除了对话: {conversation_id}")

        return {"message": "对话已删除", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="删除对话失败")
