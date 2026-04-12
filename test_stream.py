import sys
import os
sys.path.append("/workspace/backend")
import json
from app.services.ai_service import ai_service

messages = [{"role": "user", "content": "你好，请写一首短诗"}]
for chunk in ai_service.chat_stream(messages):
    print(chunk, end="")
