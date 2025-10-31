import pytest
from core.models import (
    JSONRPCRequest, JSONRPCResponse, VerseRequestParams, VerseResult, ErrorResponse,
    A2AMessage, MessagePart, TaskResult, TaskStatus, Artifact, MessageParams, ExecuteParams
)

def test_jsonrpc_request():
    # Test message/send method
    req = JSONRPCRequest(
        id="123",
        method="message/send",
        params=MessageParams(
            message=A2AMessage(
                role="user",
                parts=[MessagePart(kind="text", text="love")]
            )
        )
    )
    assert req.jsonrpc == "2.0"
    assert req.id == "123"
    assert req.method == "message/send"
    assert isinstance(req.params, MessageParams)
    assert req.params.message.parts[0].text == "love"

def test_jsonrpc_response():
    # Test with TaskResult
    task_result = TaskResult(
        id="task-123",
        contextId="ctx-123",
        status=TaskStatus(state="completed"),
        artifacts=[],
        history=[]
    )
    resp = JSONRPCResponse(id="123", result=task_result)
    assert resp.jsonrpc == "2.0"
    assert resp.id == "123"
    assert isinstance(resp.result, TaskResult)
    assert resp.result.id == "task-123"
    assert resp.error is None

def test_verse_request_params():
    params = VerseRequestParams(query="love")
    assert params.query == "love"

def test_verse_result():
    result = VerseResult(
        topic="love",
        verse_reference="John 3:16",
        verse_text="For God so loved...",
        reflection="Reflection text",
        timestamp=1234567890.0
    )
    assert result.topic == "love"
    assert result.verse_reference == "John 3:16"
    assert result.verse_text == "For God so loved..."
    assert result.reflection == "Reflection text"
    assert result.timestamp == 1234567890.0

def test_error_response():
    error = ErrorResponse(code=-32000, message="Internal error")
    assert error.code == -32000
    assert error.message == "Internal error"

def test_a2a_message():
    message = A2AMessage(
        role="user",
        parts=[MessagePart(kind="text", text="Hello world")]
    )
    assert message.role == "user"
    assert message.parts[0].kind == "text"
    assert message.parts[0].text == "Hello world"

def test_task_result():
    task_result = TaskResult(
        id="task-123",
        contextId="ctx-123",
        status=TaskStatus(state="completed"),
        artifacts=[
            Artifact(
                name="verse",
                parts=[MessagePart(kind="text", text="John 3:16")]
            )
        ],
        history=[
            A2AMessage(role="user", parts=[MessagePart(kind="text", text="love")]),
            A2AMessage(role="agent", parts=[MessagePart(kind="text", text="Here's a verse...")])
        ]
    )
    assert task_result.id == "task-123"
    assert task_result.contextId == "ctx-123"
    assert task_result.status.state == "completed"
    assert len(task_result.artifacts) == 1
    assert len(task_result.history) == 2

def test_message_params():
    params = MessageParams(
        message=A2AMessage(
            role="user",
            parts=[MessagePart(kind="text", text="love")]
        )
    )
    assert params.message.role == "user"

def test_execute_params():
    params = ExecuteParams(
        messages=[
            A2AMessage(role="user", parts=[MessagePart(kind="text", text="love")])
        ],
        contextId="ctx-123",
        taskId="task-123"
    )
    assert len(params.messages) == 1
    assert params.contextId == "ctx-123"
    assert params.taskId == "task-123"
