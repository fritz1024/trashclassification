"""
AI聊天服务 - 通义千问 + RAG + Function Calling
"""
import dashscope
from dashscope import Generation
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict
import json
import urllib.request
import urllib.parse
from app.core.database import SessionLocal
from app.models.database import Prediction, User
from sqlalchemy import func


# 定义可供大模型调用的工具列表
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_prediction_history",
            "description": "获取当前用户的垃圾分类识别历史记录。当用户问'我识别过什么垃圾'、'我的识别历史'等时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回的记录数量，默认为5",
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_stats",
            "description": "获取系统全局统计数据。当用户问'系统有多少用户'、'大家都在识别什么垃圾'、'系统总共识别了多少次'时调用。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "从系统的向量知识库中检索特定的垃圾分类和环保知识。当用户询问专业分类标准、处理流程时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要检索的关键词或问题",
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def get_user_prediction_history(user_id: int, limit: int = 5) -> str:
    """查询用户的识别历史（工具函数）"""
    if not user_id:
        return "请先登录后再查询识别历史。"
        
    db = SessionLocal()
    try:
        predictions = db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        
        if not predictions:
            return "您还没有进行过垃圾分类识别。"
            
        result = []
        for p in predictions:
            time_str = p.created_at.strftime("%Y-%m-%d %H:%M:%S")
            result.append(f"在 {time_str} 识别了：{p.predicted_class} (置信度: {p.confidence}%)")
            
        return "\n".join(result)
    except Exception as e:
        logger.error(f"查询历史失败: {e}")
        return "查询识别历史时发生错误。"
    finally:
        db.close()

def get_global_stats() -> str:
    """获取系统全局统计数据（工具函数）"""
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_predictions = db.query(Prediction).count()
        
        # 获取Top3最常识别的垃圾
        top_classes = db.query(
            Prediction.predicted_class, 
            func.count(Prediction.id).label('count')
        ).group_by(Prediction.predicted_class).order_by(func.count(Prediction.id).desc()).limit(3).all()
        
        top_str = "、".join([f"{c[0]}({c[1]}次)" for c in top_classes])
        
        return f"系统当前共有 {total_users} 名注册用户，累计完成 {total_predictions} 次垃圾识别。大家最常识别的垃圾类别是：{top_str}。"
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return "获取系统统计数据时发生错误。"
    finally:
        db.close()


class AIService:
    """AI聊天服务类（ReAct Agent）"""

    def __init__(self):
        """初始化AI服务"""
        if settings.DASHSCOPE_API_KEY:
            dashscope.api_key = settings.DASHSCOPE_API_KEY
        else:
            logger.warning("未配置 DASHSCOPE_API_KEY，AI聊天功能将不可用")

        # 立即加载向量数据库
        self.vector_store = None
        try:
            from app.services.vector_store import vector_store
            self.vector_store = vector_store
            logger.info("向量数据库已加载")
        except Exception as e:
            logger.warning(f"向量数据库加载失败: {str(e)}")

    def search_knowledge_base(self, query: str) -> str:
        """从向量数据库检索（工具函数）"""
        if not settings.ENABLE_RAG or self.vector_store is None:
            return "知识库未开启或不可用。"
            
        try:
            results = self.vector_store.search(query, n_results=3)
            if not results:
                return "在知识库中没有找到相关信息。"
                
            context_parts = []
            for i, doc in enumerate(results, 1):
                context_parts.append(f"片段 {i}:\n{doc['content']}")
            return "\n\n".join(context_parts)
        except Exception as e:
            logger.error(f"检索知识库失败: {e}")
            return "检索知识库时发生错误。"

    def chat(self, messages: List[Dict[str, str]], user_id: int = None) -> str:
        """
        调用通义千问API进行对话（集成 Function Calling）
        
        注意：此处不支持原生 stream 流式输出与 Function Calling 同步混合使用，
        因此若触发了工具调用，将强制以同步方式完成所有链式请求后再返回。
        """
        if not settings.DASHSCOPE_API_KEY:
            return "AI聊天功能未配置，请联系管理员添加 DASHSCOPE_API_KEY"

        try:
            system_content = """你是一个专业的垃圾分类助手和平台向导，具有以下特点和限制：
1. 你可以回答垃圾分类、环保、资源回收等问题。
2. 你是一个 ReAct Agent，你可以通过调用工具（Tools）来获取系统数据或检索知识库。
3. 当用户询问其个人的识别记录时，调用 get_user_prediction_history。
4. 当用户询问系统整体的运行情况、用户量、识别总量时，调用 get_global_stats。
5. 当用户询问复杂的分类标准或处理流程时，优先调用 search_knowledge_base 检索专业知识。
6. 如果用户的请求无关环保和系统（如写代码、算数），请委婉拒绝。
"""
            # 准备请求消息
            current_messages = [{"role": "system", "content": system_content}] + messages

            # 第一次调用大模型，附带 tools
            response = Generation.call(
                model='qwen-plus', # qwen-turbo 对 tools 支持可能不稳定，建议用 plus
                messages=current_messages,
                tools=TOOLS,
                result_format='message'
            )

            if response.status_code != 200:
                logger.error(f"API调用失败: {response.code} - {response.message}")
                return f"抱歉，AI服务暂时不可用。错误信息: {response.message}"

            assistant_msg = response.output.choices[0].message
            current_messages.append(assistant_msg)

            # 检查模型是否决定调用工具
            if hasattr(assistant_msg, 'tool_calls') and assistant_msg.tool_calls:
                # 遍历所有工具调用请求
                for tool_call in assistant_msg.tool_calls:
                    func_name = tool_call.function.name
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except:
                        func_args = {}
                        
                    logger.info(f"Agent 决定调用工具: {func_name}, 参数: {func_args}")
                    
                    # 执行对应的本地工具函数
                    tool_result = ""
                    if func_name == "get_user_prediction_history":
                        limit = func_args.get("limit", 5)
                        tool_result = get_user_prediction_history(user_id, limit)
                    elif func_name == "get_global_stats":
                        tool_result = get_global_stats()
                    elif func_name == "search_knowledge_base":
                        query = func_args.get("query", "")
                        tool_result = self.search_knowledge_base(query)
                    else:
                        tool_result = f"未知的工具: {func_name}"

                    # 将工具的执行结果追加到消息列表中
                    current_messages.append({
                        "role": "tool",
                        "name": func_name,
                        "content": tool_result
                    })
                
                # 第二次调用大模型，让它基于工具的返回结果生成最终回答
                second_response = Generation.call(
                    model='qwen-plus',
                    messages=current_messages,
                    result_format='message'
                )
                
                if second_response.status_code == 200:
                    return second_response.output.choices[0].message.content
                else:
                    return f"基于工具结果生成回答时失败: {second_response.message}"
            
            # 如果没有调用工具，直接返回模型的自然语言回复
            return assistant_msg.content

        except Exception as e:
            logger.error(f"AI Agent 运行异常: {str(e)}", exc_info=True)
            return f"抱歉，处理您的请求时出现错误: {str(e)}"


# 创建全局AI服务实例
ai_service = AIService()
