import requests
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.bible_api import get_daily_verse
from core.ai_service import generate_reflection
from core.config import DAILY_POST_TIME, TELEX_BASE_URL, TELEX_WEBHOOK_HOOK_ID, TELEX_BEARER_TOKEN
import logging

logger = logging.getLogger(__name__)

def post_daily_verse():
    """
    Function to post the daily verse to Telex via A2A webhook.
    """
    try:
        verse = get_daily_verse()
        reflection = generate_reflection(verse.verse_text, verse.topic)
        verse.reflection = reflection

        # Prepare A2A message payload for Telex webhook
        a2a_payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4().hex),
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "role": "agent",
                    "parts": [
                        {
                            "kind": "text",
                            "text": f"📖 **Daily Bible Verse**\n\n**{verse.verse_reference}**\n{verse.verse_text}\n\n💭 *{verse.reflection}*",
                            "metadata": None
                        }
                    ],
                    "messageId": str(uuid.uuid4().hex),
                    "contextId": None,
                    "taskId": None
                },
                "metadata": None
            }
        }

        # Send to Telex A2A webhook if configured
        if TELEX_WEBHOOK_HOOK_ID and TELEX_BEARER_TOKEN:
            webhook_url = f"{TELEX_BASE_URL}/a2a/webhooks/{TELEX_WEBHOOK_HOOK_ID}"
            headers = {
                "Authorization": f"Bearer {TELEX_BEARER_TOKEN}",
                "Content-Type": "application/json"
            }
            response = requests.post(webhook_url, json=a2a_payload, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"Daily verse posted successfully: {verse.verse_reference}")
            else:
                logger.error(f"Failed to post daily verse: {response.status_code} - {response.text}")
        else:
            logger.warning("TELEX_WEBHOOK_HOOK_ID or TELEX_BEARER_TOKEN not configured, logging verse instead")
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
