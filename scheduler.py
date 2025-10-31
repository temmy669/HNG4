from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.bible_api import get_daily_verse
from core.ai_service import generate_reflection
from core.config import DAILY_POST_TIME
import logging

logger = logging.getLogger(__name__)

def post_daily_verse():
    """
    Function to post the daily verse. In a real Telex integration, this would send to the channel.
    For now, just log it.
    """
    try:
        verse = get_daily_verse()
        reflection = generate_reflection(verse.verse_text, verse.topic)
        verse.reflection = reflection
        # Simulate posting to Telex channel
        logger.info(f"Daily Verse: {verse.verse_reference} - {verse.verse_text} - Reflection: {verse.reflection}")
        # In real implementation: send to TELEX_BASE_URL with CHANNEL_ID
    except Exception as e:
        logger.error(f"Error posting daily verse: {e}")

def setup_scheduler():
    """
    Set up the APScheduler for daily verse posting.
    """
    scheduler = AsyncIOScheduler()
    hour, minute = DAILY_POST_TIME.split(":")
    trigger = CronTrigger(hour=int(hour), minute=int(minute))
    scheduler.add_job(post_daily_verse, trigger=trigger, id="daily_verse", name="Post Daily Verse")
    return scheduler
