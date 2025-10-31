import os
import google.generativeai as genai
from .config import GEMINI_API_KEY
from .models import VerseResult, A2AMessage, TaskResult, TaskStatus, Artifact, MessagePart
from .bible_api import get_verse_by_topic
import logging
from uuid import uuid4

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
logger = logging.getLogger(__name__)

def extract_topic(query: str) -> str:
    """
    Use AI to extract the main topic from the user's query.
    """
    prompt = f"Extract the main topic or keyword from this query: '{query}'. Respond with a comma separated list of words."
    response = model.generate_content(prompt)
    topic = response.text.strip()
    return topic

def generate_reflection(verse_text: str, topic: str) -> str:
    """
    Generate a one-sentence reflection on the verse.
    """
    prompt = f"Provide a one-sentence reflection on this Bible verse related to {topic}: '{verse_text}'"
    response = model.generate_content(prompt)
    reflection = response.text.strip()
    return reflection

def process_verse_request(query: str) -> VerseResult:
    """
    Full pipeline: extract topic, get verse, add reflection.
    """
    topic = extract_topic(query)
    verse = get_verse_by_topic(topic)  # From bible_api
    reflection = generate_reflection(verse.verse_text, topic)
    verse.reflection = reflection
    return verse

async def process_messages(
    messages: list[A2AMessage],
    context_id: str,
    task_id: str,
    config: dict = None
) -> TaskResult:
    """
    Process A2A messages and return TaskResult for verse requests.
    This is the main entry point for A2A protocol processing.
    """
    logger.info(f"Processing messages for context {context_id}, task {task_id}")

    # Extract last user message
    user_message = messages[-1] if messages else None
    if not user_message:
        logger.error("No message provided in messages")
        raise ValueError("No message provided")

    # Extract query from message parts
    query = ""
    for part in user_message.parts:
        if part.kind == "text":
            query = part.text.strip()
            break

    if not query:
        logger.error("No text query found in message parts")
        raise ValueError("No text query found in message")

    logger.info(f"Processing verse request: {query}")

    # Process the verse request (using existing logic)
    verse_result = process_verse_request(query)

    # Build response message
    response_text = f"Here's a verse on '{verse_result.topic}':\n\n{verse_result.verse_reference}\n{verse_result.verse_text}"
    if verse_result.reflection:
        response_text += f"\n\nReflection: {verse_result.reflection}"

    response_message = A2AMessage(
        role="agent",
        parts=[MessagePart(kind="text", text=response_text)],
        taskId=task_id
    )

    # Build artifacts
    artifacts = [
        Artifact(
            name="verse",
            parts=[
                MessagePart(kind="text", text=verse_result.verse_text),
                MessagePart(kind="data", data={
                    "reference": verse_result.verse_reference,
                    "topic": verse_result.topic,
                    "reflection": verse_result.reflection,
                    "timestamp": verse_result.timestamp
                })
            ]
        )
    ]

    # Build history
    history = messages + [response_message]

    # Determine state (completed since it's a single-turn task)
    state = "completed"

    return TaskResult(
        id=task_id,
        contextId=context_id,
        status=TaskStatus(
            state=state,
            message=response_message
        ),
        artifacts=artifacts,
        history=history
    )
