import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.bible_api import get_daily_verse
from core.ai_service import generate_reflection
from core.config import DAILY_POST_TIME, TELEX_WEBHOOK_URL, TELEX_CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

def post_daily_verse():
    """
    Function to post the daily verse to Telex via webhook.
    """
    try:
        verse = get_daily_verse()
        reflection = generate_reflection(verse.verse_text, verse.topic)
        verse.reflection = reflection

        # Prepare message for Telex webhook
        message = {
            "event_name": "daily_verse",
            "message": f"📖 **Daily Bible Verse**\n\n**{verse.verse_reference}**\n{verse.verse_text}\n\n💭 *{verse.reflection}*",
            "status": "success",
            "username": "Bible Verse Bot"
        }

        # Send to Telex webhook if configured
        if TELEX_WEBHOOK_URL:
            response = requests.post(TELEX_WEBHOOK_URL, json=message, timeout=10)
            if response.status_code == 200:
                logger.info(f"Daily verse posted successfully: {verse.verse_reference}")
            else:
                logger.error(f"Failed to post daily verse: {response.status_code} - {response.text}")
        else:
            logger.warning("TELEX_WEBHOOK_URL not configured, logging verse instead")
            logger.info(f"Daily Verse: {verse.verse_reference} - {verse.verse_text} - Reflection: {verse.reflection}")

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
