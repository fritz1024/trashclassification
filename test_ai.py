import sys
import os
sys.path.append('/workspace/backend')

class MockAiService:
    def chat(self, messages, user_id=None, show_reasoning=True):
        from app.services.ai_service import ai_service
        # We need dashscope but we can't install it globally or we just mock the module?
        pass

