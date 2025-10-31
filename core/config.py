import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Bible API settings
BIBLE_API_BASE_URL = "https://labs.bible.org/api"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY")  # If required, but labs.bible.org might not need one

# Default translation
DEFAULT_TRANSLATION = "NIV"  # Can be configurable

# Scheduler settings
DAILY_POST_TIME = os.getenv("DAILY_POST_TIME") # UTC time for daily verse, e.g., 08:00

# Telex A2A settings (placeholders)
TELEX_BASE_URL = os.getenv("TELEX_BASE_URL", "https://api.telex.im")
TELEX_CHANNEL_ID = os.getenv("TELEX_CHANNEL_ID")
