"""Constants for the ChatIoT Conversation integration."""

DOMAIN = "chatiot_conversation"
INTEGRATION_VERSION = "2024.11.11"

CONF_PROVIDER = "provider"
CONF_API_KEY = "api_key"
CONF_BASE_URL = "base_url"
CONF_TEMPERATURE = "temperature"
CONF_MAX_TOKENS = "max_tokens"
CONF_ACCESS_TOKEN = "access_token"

PROVIDERS = [
    "gpt-3.5-turbo-0125",
    "gpt-4-turbo",
    "gpt-4o",
    "deepseek-chat",
    "moonshot-v1-8k"
]

DEFAULT_PROVIDER = PROVIDERS[0]
DEFAULT_API_KEY = "sk-..."
DEFAULT_BASE_URL = "https://..."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_ACCESS_TOKEN = "..."

DATA_PATH = "/config/.storage/chatiot_conversation"
WORK_PATH = "/config/custom_components/chatiot_conversation"