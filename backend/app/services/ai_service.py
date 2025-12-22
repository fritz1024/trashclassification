"""
AI聊天服务 - 通义千问
"""
import dashscope
from dashscope import Generation
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict


class AIService:
    """AI聊天服务类"""

    def __init__(self):
        """初始化AI服务"""
        if settings.DASHSCOPE_API_KEY:
            dashscope.api_key = settings.DASHSCOPE_API_KEY
        else:
            logger.warning("未配置 DASHSCOPE_API_KEY，AI聊天功能将不可用")

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """
        调用通义千问API进行对话

        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            stream: 是否使用流式输出

        Returns:
            AI的回复内容
        """
        if not settings.DASHSCOPE_API_KEY:
            return "AI聊天功能未配置，请联系管理员添加 DASHSCOPE_API_KEY"

        try:
            # 添加系统提示词，让AI专注于垃圾分类领域
            system_message = {
                "role": "system",
                "content": """你是一个专业的垃圾分类助手，具有以下特点：
1. 你精通垃圾分类知识，了解可回收物、有害垃圾、厨余垃圾、其他垃圾的分类标准
2. 你可以解答用户关于垃圾分类的各种问题
3. 你可以提供环保建议和垃圾处理方法
4. 你的回答要简洁、准确、友好
5. 当用户询问垃圾分类以外的问题时，你也可以正常回答，但会适当引导话题回到环保和垃圾分类
6. 你会用中文回答问题"""
            }

            # 构建完整的消息列表
            full_messages = [system_message] + messages

            # 调用通义千问API
            response = Generation.call(
                model='qwen-turbo',  # 使用qwen-turbo模型，速度快且免费额度充足
                messages=full_messages,
                result_format='message',
                stream=stream,
                temperature=0.7,  # 控制回答的创造性
                max_tokens=1500,  # 最大token数
            )

            if response.status_code == 200:
                # 获取AI的回复
                assistant_message = response.output.choices[0].message.content
                logger.info(f"AI回复成功，长度: {len(assistant_message)}")
                return assistant_message
            else:
                error_msg = f"API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                return f"抱歉，AI服务暂时不可用。错误信息: {response.message}"

        except Exception as e:
            logger.error(f"AI聊天服务异常: {str(e)}", exc_info=True)
            return f"抱歉，处理您的请求时出现错误: {str(e)}"


# 创建全局AI服务实例
ai_service = AIService()
