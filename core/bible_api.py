import requests
from .config import BIBLE_API_BASE_URL, DEFAULT_TRANSLATION
from .models import VerseResult
from .ai_service import generate_verse_reference
import random
import logging

logger = logging.getLogger(__name__)

def get_verse_by_topic(topic: str) -> VerseResult:
    """
    Query the Bible API for a verse related to the topic.
    First, generate a specific verse reference using AI, then fetch it.
    Fallback to random if the reference fails.
    """
    try:
        # Generate a specific verse reference
        reference = generate_verse_reference(topic)
        logger.info(f"Generated reference for topic '{topic}': {reference}")

        # Clean the reference (remove extra text if any)
        # Assume format like "John 3:16"
        url = f"{BIBLE_API_BASE_URL}/?passage={reference}&type=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                verse_data = data[0]
                verse_reference = f"{verse_data['bookname']} {verse_data['chapter']}:{verse_data['verse']}"
                verse_text = verse_data['text']
                return VerseResult(
                    topic=topic,
                    verse_reference=verse_reference,
                    verse_text=verse_text,
                    reflection=None  # Will be added by AI
                )
            else:
                logger.warning(f"No verse found for reference: {reference}")
        else:
            logger.warning(f"API error for reference {reference}: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to generate or fetch verse for topic '{topic}': {str(e)}")

    # Fallback to random verse
    logger.info(f"Falling back to random verse for topic '{topic}'")
    return get_random_verse(topic)

def get_random_verse(topic: str) -> VerseResult:
    """
    Fetch a random verse as fallback.
    """
    url = f"{BIBLE_API_BASE_URL}/?passage=random&type=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()[0]  # Assuming list
        # Ensure proper formatting: Book Chapter:Verse
        bookname = data.get('bookname', 'Unknown')
        chapter = data.get('chapter', '1')
        verse = data.get('verse', '1')
        verse_reference = f"{bookname} {chapter}:{verse}"
        verse_text = data.get('text', 'Verse text not available')
        return VerseResult(
            topic=topic,
            verse_reference=verse_reference,
            verse_text=verse_text,
            reflection=None  # Will be added by AI
        )
    else:
        raise Exception("Failed to fetch random verse from Bible API")

def get_daily_verse() -> VerseResult:
    """
    Fetch a daily verse, rotating between OT and NT if possible.
    For simplicity, random.
    """
    return get_random_verse("daily")
