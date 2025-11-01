from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from uuid import uuid4

from core.models import (
    JSONRPCRequest, JSONRPCResponse, TaskResult, TaskStatus,
    Artifact, MessagePart, A2AMessage, ErrorResponse
)
from core.ai_service import process_verse_request
from scheduler import setup_scheduler

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent state (in production, use Redis or database)
verse_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global verse_agent

    # Startup: Initialize the verse agent
    verse_agent = {}  # Simple in-memory store for contexts (sufficient for stateless agent)
    scheduler = setup_scheduler()
    scheduler.start()  # Start daily verse scheduler
    logger.info("Bible Verse Agent started")

    yield

    # Shutdown: Cleanup
    if verse_agent:
        verse_agent.clear()
    if scheduler:
        scheduler.shutdown()
    logger.info("Bible Verse Agent shut down")

app = FastAPI(
    title="Bible Verse of the Day Agent",
    description="A2A-compatible agent for retrieving Bible verses with AI reflections",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/a2a")
async def a2a_endpoint(request: Request):
    """Main A2A endpoint for verse agent"""
    logger.info(f"Received A2A request from {request.client.host if request.client else 'unknown'}")
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"Request body: {body}")

        # Validate JSON-RPC request
        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required"
                    }
                }
            )

        rpc_request = JSONRPCRequest(**body)

        # Extract messages, context, and task info
        messages = []
        context_id = None
        task_id = None
        config = {}

        # Handle different method types safely
        if hasattr(rpc_request.params, 'message'):
            # message/send method
            messages = [rpc_request.params.message]
            config = rpc_request.params.configuration.model_dump() if hasattr(rpc_request.params, 'configuration') and rpc_request.params.configuration else {}
        elif hasattr(rpc_request.params, 'messages'):
            # execute method
            messages = rpc_request.params.messages
            context_id = getattr(rpc_request.params, 'contextId', None)
            task_id = getattr(rpc_request.params, 'taskId', None)
        else:
            # Handle unknown methods gracefully
            return JSONResponse(
                status_code=200,
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_request.id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found: only 'message/send' and 'execute' are supported"
                    }
                }
            )

        # Generate IDs if not provided
        context_id = context_id or str(uuid4())
        task_id = task_id or str(uuid4())

        # Process with verse agent
        from core.ai_service import process_messages
        result = await process_messages(
            messages=messages,
            context_id=context_id,
            task_id=task_id,
            config=config
        )

        # Build response
        response = JSONRPCResponse(
            id=rpc_request.id,
            result=result
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Enhanced error handling with A2A error codes
        error_code = -32603  # Internal error
        error_message = "Internal error"
        if isinstance(e, ValueError):
            error_code = -32602  # Invalid params
            error_message = str(e)
        elif isinstance(e, KeyError):
            error_code = -32602  # Invalid params
            error_message = "Missing required parameters"

        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {
                    "code": error_code,
                    "message": error_message,
                    "data": {"details": str(e)}
                }
            }
        )

async def process_messages(
    messages: list[A2AMessage],
    context_id: str,
    task_id: str,
    config: dict = {}
) -> TaskResult:
    """Process incoming messages and generate verse response"""

    # Extract last user message
    user_message = messages[-1] if messages else None
    if not user_message:
        raise ValueError("No message provided")

    # Extract query from message parts
    query = ""
    for part in user_message.parts:
        if part.kind == "text" and part.text:
            query = part.text.strip()
            break

    if not query:
        raise ValueError("No text query found in message")

    logger.info(f"Processing verse request: {query}")

    # Process the verse request (using existing logic)
    verse_result = process_verse_request(query)

    if verse_result:
        # Build response message for verse
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
    else:
        # Handle casual chat
        response_text = "Good morning to you too!\n\nWould you like me to share a Bible verse? You can say something like: I need a verse on Love."
        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)],
            taskId=task_id
        )
        artifacts = [
            Artifact(
                name="chat_response",
                parts=[MessagePart(kind="text", text=response_text)]
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
    
@app.get("/.well-known/agent.json")
async def agent_metadata():
    """Endpoint to provide agent metadata for discovery"""
    return {
        "name": "Bible Verse of the Day Agent",
        "description": "An A2A-compatible agent that provides Bible verses with AI-generated reflections.",
        "version": "1.0.0",
        "capabilities": [
            "Retrieve Bible verses by topic",
            "Generate AI reflections on verses",
            "Daily verse posting"
        ],
        "endpoints": {
            "a2a": "/a2a"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "bible-verse"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
