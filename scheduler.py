import httpx
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.bible_api import get_daily_verse
from core.ai_service import generate_reflection
from core.config import DAILY_POST_TIME, TELEX_BASE_URL, TELEX_WEBHOOK_HOOK_ID, TELEX_BEARER_TOKEN
from core.models import TaskResult, TaskStatus, Artifact, MessagePart, A2AMessage
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def post_daily_verse():
    """
    Synchronous wrapper for the async daily verse posting.
    """
    import asyncio
    asyncio.run(post_daily_verse_async())

async def send_webhook_notification(
    webhook_url: str,
    result: TaskResult,
    auth: Optional[Dict[str, Any]] = None
):
    """Send result to webhook URL in JSON-RPC format"""
    headers = {"Content-Type": "application/json"}

    if auth and "Bearer" in auth.get("schemes", []):
        # Handle both token field and credentials field for backward compatibility
        token = auth.get("token") or auth.get("credentials")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    # Wrap TaskResult in JSON-RPC message/send format
    jsonrpc_payload = {
        "jsonrpc": "2.0",
        "id": result.id,
        "method": "message/send",
        "params": {
            "message": result.status.message.model_dump() if result.status.message else None,
            "configuration": {
                "blocking": False,
                "acceptedOutputModes": ["text/plain"],
                "pushNotificationConfig": None  # Prevent recursive webhook calls
            }
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json=jsonrpc_payload,
                headers=headers,
                timeout=30.0
            )
            logger.info(f"Webhook sent successfully to {webhook_url}, status: {response.status_code}")
            if response.status_code >= 400:
                logger.error(f"Webhook failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook_url}: {e}")

async def post_daily_verse_async():
    """
    Async function to post the daily verse to Telex via A2A webhook.
    """
    try:
        verse = get_daily_verse()
        reflection = generate_reflection(verse.verse_text, verse.topic)
        verse.reflection = reflection

        # Create TaskResult for webhook
        task_id = str(uuid.uuid4())
        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=f"📖 **Daily Bible Verse**\n\n**{verse.verse_reference}**\n{verse.verse_text}\n\n💭 *{verse.reflection}*")],
            taskId=task_id
        )

        artifacts = [
            Artifact(
                name="daily_verse",
                parts=[
                    MessagePart(kind="text", text=f"📖 **Daily Bible Verse**\n\n**{verse.verse_reference}**\n{verse.verse_text}\n\n💭 *{verse.reflection}*"),
                    MessagePart(kind="data", data={
                        "reference": verse.verse_reference,
                        "topic": verse.topic,
                        "reflection": verse.reflection,
                        "timestamp": verse.timestamp
                    })
                ]
            )
        ]

        result = TaskResult(
            id=task_id,
            contextId=str(uuid.uuid4()),
            status=TaskStatus(
                state="completed",
                message=response_message
            ),
            artifacts=artifacts,
            history=[response_message]
        )

        # Send to Telex A2A webhook if configured
        if TELEX_WEBHOOK_HOOK_ID and TELEX_BEARER_TOKEN:
            webhook_url = f"{TELEX_BASE_URL}/v1/a2a/webhooks/{TELEX_WEBHOOK_HOOK_ID}"
            auth = {"schemes": ["Bearer"], "credentials": TELEX_BEARER_TOKEN} if TELEX_BEARER_TOKEN else None
            await send_webhook_notification(webhook_url, result, auth)
            logger.info(f"Daily verse posted successfully: {verse.verse_reference}")
        else:
            # Try to use stored webhook config from incoming requests
            try:
                from main import webhook_configs
                stored_config = webhook_configs.get("default")
                if stored_config and stored_config.get('url'):
                    auth = stored_config.get('authentication')
                    await send_webhook_notification(stored_config['url'], result, auth)
                    logger.info(f"Daily verse posted to stored webhook: {verse.verse_reference}")
                else:
                    logger.warning("No webhook configuration available, logging verse instead")
                    logger.info(f"Daily Verse: {verse.verse_reference} - {verse.verse_text} - Reflection: {verse.reflection}")
            except ImportError:
                logger.warning("Could not import webhook configs, logging verse instead")
                logger.info(f"Daily Verse: {verse.verse_reference} - {verse.verse_text} - Reflection: {verse.reflection}")

    except Exception as e:
        logger.error(f"Error posting daily verse: {e}")

def setup_scheduler():
    """
    Set up the APScheduler for daily verse posting.
    """
    scheduler = AsyncIOScheduler()
    if DAILY_POST_TIME:
        hour, minute = DAILY_POST_TIME.split(":")
        trigger = CronTrigger(hour=int(hour), minute=int(minute))
        scheduler.add_job(post_daily_verse, trigger=trigger, id="daily_verse", name="Post Daily Verse")
    else:
        logger.warning("DAILY_POST_TIME not configured, scheduler not set up")
    return scheduler
