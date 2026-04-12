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
            "description": "获取当前用户的垃圾分类识别历史记录以及识别总数。当用户问'我识别过什么垃圾'、'我的识别历史'、'我识别了多少记录'等时调用。",
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
            "name": "get_current_user_info",
            "description": "获取当前登录用户的基本信息，如用户名、角色、注册时间等。当用户问'我是谁'、'我的信息'等时调用。",
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
            "description": "搜索垃圾分类或环保相关的专业知识库。当用户询问具体的垃圾分类规则、政策、科普知识或如何处理某种垃圾时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def search_knowledge_base(query: str, vector_store) -> str:
    """搜索知识库（工具函数）"""
    if not query:
        return "请提供有效的搜索关键词。"
    if not vector_store:
        return "知识库当前不可用。"
        
    try:
        results = vector_store.search(query)
        if not results:
            return "知识库中未找到相关内容。"
            
        docs = []
        for i, res in enumerate(results):
            content = res.get('content', '')
            docs.append(f"文档片段 {i+1}:\n{content}")
            
        return "\n\n---\n\n".join(docs)
    except Exception as e:
        logger.error(f"知识库搜索失败: {e}")
        return "搜索知识库时发生错误。"

def get_user_prediction_history(user_id: int, limit: int = 5) -> str:
    """查询用户的识别历史（工具函数）"""
    if not user_id:
        return "请先登录后再查询识别历史。"
        
    db = SessionLocal()
    try:
        total_count = db.query(Prediction).filter(Prediction.user_id == user_id).count()
        
        predictions = db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        
        if not predictions:
            return "您还没有进行过垃圾分类识别。"
            
        result = [f"您总共进行了 {total_count} 次垃圾分类识别。以下是最近的 {len(predictions)} 次记录："]
        for p in predictions:
            time_str = p.created_at.strftime("%Y-%m-%d %H:%M:%S")
            result.append(f"在 {time_str} 识别了：{p.predicted_class} (置信度: {p.confidence}%)")
            
        return "\n".join(result)
    except Exception as e:
        logger.error(f"查询历史失败: {e}")
        return "查询识别历史时发生错误。"
    finally:
        db.close()

def get_current_user_info(user_id: int) -> str:
    """获取当前登录用户信息（工具函数）"""
    if not user_id:
        return "您当前是游客/匿名用户，未登录系统。"
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "未能找到您的用户记录。"
            
        time_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        role_str = "管理员" if user.role in ["admin", "super_admin"] else "普通用户"
        
        return f"您的用户名是：{user.username}\n您的角色是：{role_str}\n您的注册时间是：{time_str}\n邮箱：{user.email or '未绑定'}"
    except Exception as e:
        logger.error(f"查询用户信息失败: {e}")
        return "查询用户信息时发生错误。"
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

    def chat(self, messages: List[Dict[str, str]], user_id: int = None, show_reasoning: bool = True) -> str:
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
2. 你是一个 ReAct Agent，你可以通过调用工具（Tools）来获取系统数据，搜索内部知识库，或利用联网功能检索最新知识。
3. 当用户询问具体的垃圾分类规则、政策、科普知识或如何处理某种垃圾时，调用 search_knowledge_base 搜索知识库。
4. 当用户询问其个人的识别记录时，调用 get_user_prediction_history。
5. 当用户询问系统整体的运行情况、用户量、识别总量时，调用 get_global_stats。
6. 当用户询问'我是谁'、'我的信息'等个人资料时，调用 get_current_user_info。
7. 如果用户的请求无关环保和系统（如写代码、算数），请委婉拒绝。
"""
            # 准备请求消息
            current_messages = [{"role": "system", "content": system_content}] + messages

            # 第一次调用大模型，附带 tools
            response = Generation.call(
                model='qwen-plus', # qwen-turbo 对 tools 支持可能不稳定，建议用 plus
                messages=current_messages,
                tools=TOOLS,
                result_format='message',
                enable_search=True
            )

            if response.status_code != 200:
                logger.error(f"API调用失败: {response.code} - {response.message}")
                return f"抱歉，AI服务暂时不可用。错误信息: {response.message}"

            assistant_msg = response.output.choices[0].message
            current_messages.append(assistant_msg)

            reasoning_steps = []

            # 检查模型是否决定调用工具
            if assistant_msg.get('tool_calls'):
                # 如果模型在调用工具前有输出思考过程
                if getattr(assistant_msg, 'content', None):
                    reasoning_steps.append(f"🧠 **思考**: {assistant_msg.content}")

                # 遍历所有工具调用请求
                for tool_call in assistant_msg.tool_calls:
                    # Dashscope 返回的 tool_call 可能是 dict
                    if isinstance(tool_call, dict):
                        func_name = tool_call.get('function', {}).get('name', '')
                        try:
                            func_args_str = tool_call.get('function', {}).get('arguments', '{}')
                            func_args = json.loads(func_args_str)
                        except:
                            func_args = {}
                    else:
                        func_name = tool_call.function.name
                        try:
                            func_args = json.loads(tool_call.function.arguments)
                        except:
                            func_args = {}
                        
                    logger.info(f"Agent 决定调用工具: {func_name}, 参数: {func_args}")
                    reasoning_steps.append(f"🛠️ **行动 (Action)**: 调用工具 `{func_name}`，参数: `{func_args}`")
                    
                    # 执行对应的本地工具函数
                    tool_result = ""
                    if func_name == "get_user_prediction_history":
                        limit = func_args.get("limit", 5)
                        tool_result = get_user_prediction_history(user_id, limit)
                    elif func_name == "get_global_stats":
                        tool_result = get_global_stats()
                    elif func_name == "get_current_user_info":
                        tool_result = get_current_user_info(user_id)
                    elif func_name == "search_knowledge_base":
                        query = func_args.get("query", "")
                        tool_result = search_knowledge_base(query, self.vector_store)
                    else:
                        tool_result = f"未知的工具: {func_name}"

                    reasoning_steps.append(f"📄 **观察 (Observation)**: {tool_result}")

                    # 将工具的执行结果追加到消息列表中
                    # 在 dashscope 中如果使用 OpenAI 兼容模式或 dict，工具结果格式可能不同
                    if isinstance(tool_call, dict):
                        current_messages.append({
                            "role": "tool",
                            "name": func_name,
                            "content": tool_result
                        })
                    else:
                        current_messages.append({
                            "role": "tool",
                            "name": func_name,
                            "content": tool_result
                        })
                
                # 第二次调用大模型，让它基于工具的返回结果生成最终回答
                second_response = Generation.call(
                    model='qwen-plus',
                    messages=current_messages,
                    result_format='message',
                    enable_search=True
                )
                
                if second_response.status_code == 200:
                    final_answer = second_response.output.choices[0].message.content
                    if show_reasoning and reasoning_steps:
                        reasoning_text = "\n".join([f"> {step}" for step in reasoning_steps])
                        return f"{reasoning_text}\n\n**最终回答**:\n{final_answer}"
                    else:
                        return final_answer
                else:
                    return f"基于工具结果生成回答时失败: {second_response.message}"
            
            # 如果没有调用工具，直接返回模型的自然语言回复
            return assistant_msg.content

        except Exception as e:
            logger.error(f"AI Agent 运行异常: {str(e)}", exc_info=True)
            return f"抱歉，处理您的请求时出现错误: {str(e)}"


# 创建全局AI服务实例
ai_service = AIService()
