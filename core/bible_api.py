import requests
from .config import BIBLE_API_BASE_URL, BIBLE_API_KEY, BIBLE_ID
from .models import VerseResult
import random
import re

def get_verse_by_topic(topic: str) -> VerseResult:
    """
    Query the Bible API for a verse related to the topic using api.bible search.
    """
    headers = {"api-key": BIBLE_API_KEY}

    # First, search for passages related to the topic
    search_url = f"{BIBLE_API_BASE_URL}/bibles/{BIBLE_ID}/search"
    params = {
        "query": topic,
        "limit": 10,
        "sort": "relevance"
    }

    try:
        search_response = requests.get(search_url, headers=headers, params=params)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("data", {}).get("passages"):
                # Get a random passage from search results
                passages = search_data["data"]["passages"]
                passage = random.choice(passages)

                # Extract verse details
                reference = passage["reference"]
                content = passage["content"]

                # Clean up HTML tags from content
                clean_content = re.sub(r'<[^>]+>', '', content)

                return VerseResult(
                    topic=topic,
                    verse_reference=reference,
                    verse_text=clean_content.strip(),
                    reflection=None  # Will be added by AI
                )

        # Fallback: get a random verse if search fails
        return get_random_verse(topic)

    except Exception as e:
        print(f"Search failed: {e}")
        return get_random_verse(topic)

def get_random_verse(topic: str) -> VerseResult:
    """
    Fallback: Get a random verse from the Bible.
    """
    headers = {"api-key": BIBLE_API_KEY}

    # Get books first
    books_url = f"{BIBLE_API_BASE_URL}/bibles/{BIBLE_ID}/books"
    books_response = requests.get(books_url, headers=headers)

    if books_response.status_code == 200:
        books = books_response.json()["data"]
        book = random.choice(books)

        # Get chapters for the selected book
        chapters_url = f"{BIBLE_API_BASE_URL}/bibles/{BIBLE_ID}/books/{book['id']}/chapters"
        chapters_response = requests.get(chapters_url, headers=headers)

        if chapters_response.status_code == 200:
            chapters = chapters_response.json()["data"]
            chapter = random.choice(chapters)

            # Get verses for the selected chapter
            verses_url = f"{BIBLE_API_BASE_URL}/bibles/{BIBLE_ID}/chapters/{chapter['id']}/verses"
            verses_response = requests.get(verses_url, headers=headers)

            if verses_response.status_code == 200:
                verses = verses_response.json()["data"]
                verse = random.choice(verses)

                # Get the actual verse content
                verse_url = f"{BIBLE_API_BASE_URL}/bibles/{BIBLE_ID}/verses/{verse['id']}"
                verse_response = requests.get(verse_url, headers=headers, params={"include-chapter-numbers": "false"})

                if verse_response.status_code == 200:
                    verse_data = verse_response.json()["data"]
                    reference = verse_data["reference"]
                    content = verse_data["content"]

                    # Clean up HTML tags
                    clean_content = re.sub(r'<[^>]+>', '', content)

                    return VerseResult(
                        topic=topic,
                        verse_reference=reference,
                        verse_text=clean_content.strip(),
                        reflection=None
                    )

    raise Exception("Failed to fetch verse from Bible API")

def get_daily_verse() -> VerseResult:
    """
    Fetch a daily verse, rotating between OT and NT if possible.
    For simplicity, random.
    """
    return get_random_verse("daily")
