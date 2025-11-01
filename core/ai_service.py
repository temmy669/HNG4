import os
import google.generativeai as genai
from .config import GEMINI_API_KEY
from .models import VerseResult, A2AMessage, TaskResult, TaskStatus, Artifact, MessagePart
import logging
from uuid import uuid4

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
logger = logging.getLogger(__name__)

def extract_topic(query: str) -> str:
    """
    Use AI to detect if user wants a Bible verse or is just chatting.
    If no verse is needed, return a special marker: '__NO_VERSE__'
    """
    prompt = f"""
    Decide the user's intent from this message: '{query}'.

    If they are just greeting, chatting or not asking for a Bible verse:
    - Reply with exactly: __NO_VERSE__

    If they are asking for a Bible verse, Bible topic, or scripture:
    - Reply with only the main topic word(s)
    - If two topics, separate them with a comma.
    - No extra words, no explanations.
    """

    response = model.generate_content(prompt).text.strip()
    return response

def generate_verse_reference(topic: str) -> str:
    """
    Generate a valid Bible verse reference related to the topic.
    """
    prompt = f"Give only a valid Bible verse reference about {topic}. Format: Book Chapter:Verse."
    response = model.generate_content(prompt).text.strip()
    return response


def generate_reflection(verse_text: str, topic: str) -> str:
    """
    Generate a one-sentence reflection on the verse.
    """
    try:
        prompt = f"Encourage the user and Provide a one-sentence reflection on this Bible verse related to {topic}: '{verse_text}'"
        response = model.generate_content(prompt)
        reflection = response.text.strip()
        return reflection
    except Exception as e:
        logger.error(f"Failed to generate reflection: {str(e)}")
        return f"This verse speaks to the importance of {topic} in our spiritual journey."

def process_verse_request(query: str):
    from .bible_api import get_verse_by_topic  # Import here to avoid circular import

    topic = extract_topic(query)

    if topic == "__NO_VERSE__":
        return None  # Signal that it's just chat.

    verse = get_verse_by_topic(topic)
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
    if verse_result:
        response_text = f"Here's what i found:\n{verse_result.verse_reference}\n{verse_result.verse_text}"
        if verse_result.reflection:
            response_text += f"\n\nReflection: {verse_result.reflection}"

        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)],
            taskId=task_id
        )
    else:
        # Just casual chat reply
        #generate model response based of user query
            response = model.generate_content(
                            f"You are a friendly assistant. Reply briefly and naturally to this message: '{query}'. \
                        If they didn't ask for a Bible verse, respond casually and at the end politely ask: \
                        'Would you like me to share a Bible verse? You can say something like: I need a verse on Love.' \
                        Keep your tone warm, concise, and human-like."
                        )
            response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response.text.strip())],
            taskId=task_id
        )


   

    # Build artifacts
    if verse_result:
        artifacts = [
            Artifact(
                name="verse",
                parts=[
                    MessagePart(
                        kind="text",
                        text=(
                            f"📖 *Here's what i found:*\n\n"
                            f"{verse_result.verse_reference}\n"
                            f"{verse_result.verse_text}\n\n"
                            f"🕊️ Reflection: {verse_result.reflection}"
                        )
                    ),
                    MessagePart(
                        kind="data",
                        data={
                            "reference": verse_result.verse_reference,
                            "topic": verse_result.topic,
                            "reflection": verse_result.reflection,
                            "timestamp": verse_result.timestamp
                        }
                    )

                ]
            )
        ]
    elif not verse_result:
        artifacts = [
            Artifact(
                name="chat_response",
                parts=[
                    MessagePart(
                        kind="text",
                        text=response_message.parts[0].text
                    )
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
