import sys
import os
sys.path.append('/workspace/backend')

from app.services.ai_service import ai_service

if __name__ == "__main__":
    messages = [{"role": "user", "content": "我的识别历史有哪些？"}]
    # 模拟 user_id=1
    response = ai_service.chat(messages, user_id=1)
    print("AI Response:\n", response)
