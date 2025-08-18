import os
from dotenv import load_dotenv

load_dotenv()

# Retrieve environment variables else throw an error
def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"{name} is not set")
    return val.strip()

BOT_API_KEY = require_env("BOT_API_KEY")
LLM_ENDPOINT = require_env("LLM_ENDPOINT").rstrip("/")
LLM_API_KEY = require_env("LLM_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL")  # optional; ConversationBuilder will use it

LLM_HEADERS = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json",
}

LLM_CHAT_URL = f"{LLM_ENDPOINT}/chat/completions"
LLM_MODELS_URL = f"{LLM_ENDPOINT}/models"

# General constants
DISCORD_MAX = 2000
THINK_MARKER = "</think>"