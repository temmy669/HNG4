import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Bible API settings (using api.bible for better search support)
BIBLE_API_BASE_URL = "https://api.scripture.api.bible/v1"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY")  # Required for api.bible
BIBLE_ID = "de4e12af7f28f599-02"  # NIV translation ID on api.bible

# Default translation
DEFAULT_TRANSLATION = "NIV"  # Can be configurable

# Scheduler settings
DAILY_POST_TIME = os.getenv("DAILY_POST_TIME") # UTC time for daily verse, e.g., 08:00

# Telex A2A settings
TELEX_BASE_URL = os.getenv("TELEX_BASE_URL", "https://api.telex.im")
TELEX_WEBHOOK_HOOK_ID = os.getenv("TELEX_WEBHOOK_HOOK_ID")  # The {hookId} from webhook URL
TELEX_BEARER_TOKEN = os.getenv("TELEX_BEARER_TOKEN")  # Bearer token for authentication
