import sys
sys.path.append("/workspace/backend")
from app.core.config import settings
import dashscope
dashscope.api_key = settings.DASHSCOPE_API_KEY
from dashscope import Generation

responses = Generation.call(
    model='qwen-plus',
    messages=[{"role": "user", "content": "你好，请写一首短诗"}],
    result_format='message',
    stream=True,
    incremental_output=True
)

for r in responses:
    if r.status_code == 200:
        print(r.output.choices[0].message.content, end="", flush=True)
    else:
        print("Error:", r.message)
