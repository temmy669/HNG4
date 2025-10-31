import requests
from .config import BIBLE_API_BASE_URL, DEFAULT_TRANSLATION
from .models import VerseResult
import random

def get_verse_by_topic(topic: str) -> VerseResult:
    """
    Query the Bible API for a verse related to the topic.
    For simplicity, we'll use a search endpoint if available, or fetch a random verse.
    labs.bible.org API: https://labs.bible.org/api_web_service
    Example: https://labs.bible.org/api/?passage=random&type=json
    Or search: https://labs.bible.org/api/?passage=John%203:16&type=json
    But for topic, we might need to map topics to passages or use search.
    Since it's free, we'll simulate by fetching a random verse and assuming it matches.
    In real implementation, use a better API like api.bible which supports search.
    """
    # For demo, fetch a random verse
    url = f"{BIBLE_API_BASE_URL}/?passage=random&type=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()[0]  # Assuming list
        verse_reference = f"{data['bookname']} {data['chapter']}:{data['verse']}"
        verse_text = data['text']
        return VerseResult(
            topic=topic,
            verse_reference=verse_reference,
            verse_text=verse_text,
            reflection=None  # Will be added by AI
        )
    else:
        raise Exception("Failed to fetch verse from Bible API")

def get_daily_verse() -> VerseResult:
    """
    Fetch a daily verse, rotating between OT and NT if possible.
    For simplicity, random.
    """
    return get_verse_by_topic("daily")
