print("Config package initialized.")

DEBUG = True

# MODEL ------------------------------------------------------------------------

# 支持OpenAI规范接口
LLM_URL = 'https://api.3ren.cn/ai-paas-platform/ai/base/chat'
LLM_appToken = 'SEysWctCnOIRkkzvhtm3mfcHmU5'
LLM_appCode = 'test-only'

GPT_URL = 'https://api.openai.com/v1/chat/completions'
MODEL = 'gpt-3.5-turbo'
API_KEY = 'sk-xxxxxx'
SYSTEM_PROMPT = 'You are a helpful assistant.'


# MODEL ------------------------------------------------------------------------

# CONFIGURATION ------------------------------------------------------------------------

# 意图相关性判断阈值0-1
RELATED_INTENT_THRESHOLD = 0.5

# CONFIGURATION ------------------------------------------------------------------------
