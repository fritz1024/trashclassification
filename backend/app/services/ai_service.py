"""
AI聊天服务 - 通义千问 + RAG
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

        # 延迟加载向量数据库（避免启动时加载模型）
        self._vector_store = None

    @property
    def vector_store(self):
        """懒加载向量数据库"""
        if self._vector_store is None:
            try:
                from app.services.vector_store import vector_store
                self._vector_store = vector_store
                logger.info("向量数据库已加载")
            except Exception as e:
                logger.warning(f"向量数据库加载失败: {str(e)}")
                self._vector_store = None
        return self._vector_store

    def retrieve_context(self, query: str) -> str:
        """
        从向量数据库检索相关上下文

        Args:
            query: 用户查询

        Returns:
            相关文档内容
        """
        try:
            if self.vector_store is None:
                return ""

            # 检索相关文档
            results = self.vector_store.search(query, n_results=3)

            if not results:
                return ""

            # 组合检索到的文档
            context_parts = []
            for i, doc in enumerate(results, 1):
                context_parts.append(f"参考文档 {i}:\n{doc['content']}\n")

            context = "\n".join(context_parts)
            logger.info(f"检索到 {len(results)} 个相关文档，总长度: {len(context)}")

            return context

        except Exception as e:
            logger.error(f"检索上下文失败: {str(e)}", exc_info=True)
            return ""

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """
        调用通义千问API进行对话（集成 RAG）

        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            stream: 是否使用流式输出

        Returns:
            AI的回复内容
        """
        if not settings.DASHSCOPE_API_KEY:
            return "AI聊天功能未配置，请联系管理员添加 DASHSCOPE_API_KEY"

        try:
            # 获取最后一条用户消息
            last_user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break

            # 从向量数据库检索相关上下文
            context = self.retrieve_context(last_user_message)

            # 构建系统提示词
            system_content = """你是一个专业的垃圾分类助手和平台向导，具有以下特点和限制：

【你的专业领域】
1. 垃圾分类知识：可回收物、有害垃圾、厨余垃圾、其他垃圾的分类标准和识别方法
2. 环保知识：环境保护、资源回收、减少污染、可持续发展等相关内容
3. 垃圾处理：各类垃圾的正确处理方法、回收流程、注意事项
4. 平台向导：本垃圾分类识别系统的功能介绍、使用教程、操作指南

【回答原则】
1. 只回答与垃圾分类、环保、本系统使用相关的问题
2. 对于无关问题（如编程、数学、历史、娱乐等），礼貌地拒绝并引导用户提问相关话题
3. 回答要简洁、准确、友好，使用中文
4. 可以适当科普环保知识，提高用户的环保意识
5. 当用户询问平台功能时，优先参考下面提供的【参考文档】中的信息，确保准确性
6. 如果参考文档中没有相关信息，可以基于你的知识回答垃圾分类和环保问题

【拒绝回答示例】
当用户问"今天天气怎么样"、"帮我写代码"、"1+1等于几"等无关问题时，你应该回复：
"抱歉，我是专门的垃圾分类助手和平台向导，只能回答垃圾分类、环保和本系统使用相关的问题。您可以问我：
- 某种物品属于什么垃圾？
- 如何正确处理某类垃圾？
- 垃圾分类的标准是什么？
- 如何使用本系统的识别功能？
- 平台有哪些功能？
等等。有什么垃圾分类或平台使用方面的问题我可以帮您解答吗？"
"""

            # 如果检索到了相关文档，添加到系统提示词中
            if context:
                system_content += f"\n\n【参考文档】\n以下是从项目文档中检索到的相关信息，请优先参考这些内容回答用户问题：\n\n{context}"

            system_message = {
                "role": "system",
                "content": system_content
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
