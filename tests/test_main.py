import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app
from core.models import JSONRPCResponse, VerseResult, A2AMessage, MessagePart, TaskResult, TaskStatus, MessageParams

@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")

@pytest.mark.asyncio
async def test_valid_message_send_request(client):
    with patch('ai_service.process_verse_request') as mock_process:
        mock_verse = VerseResult(
            topic="love",
            verse_reference="1 John 4:8",
            verse_text="Whoever does not love does not know God, because God is love.",
            reflection="This verse reminds us that love is the essence of God's nature.",
            timestamp=1735148400.0
        )
        mock_process.return_value = mock_verse

        response = await client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "123",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Get a verse on love"}]
                }
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "123"
        assert "result" in data
        assert isinstance(data["result"], dict)
        assert "id" in data["result"]
        assert "contextId" in data["result"]
        assert "status" in data["result"]
        assert "artifacts" in data["result"]
        assert "history" in data["result"]

@pytest.mark.asyncio
async def test_invalid_jsonrpc_request(client):
    response = await client.post("/a2a", json={
        "jsonrpc": "2.0",
        "id": "123",
        "method": "invalid_method",
        "params": {}
    })

    assert response.status_code == 500  # Pydantic validation error
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32602  # Invalid params due to validation

@pytest.mark.asyncio
async def test_missing_params(client):
    response = await client.post("/a2a", json={
        "jsonrpc": "2.0",
        "id": "123",
        "method": "message/send",
        "params": {}
    })

    assert response.status_code == 500  # Pydantic validation error
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32602  # Invalid params due to validation

@pytest.mark.asyncio
async def test_ai_service_failure(client):
    with patch('ai_service.process_verse_request', side_effect=Exception("AI service error")):
        response = await client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "123",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "love"}]
                }
            }
        })

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32603  # Internal error

@pytest.mark.asyncio
async def test_execute_method(client):
    with patch('ai_service.process_verse_request') as mock_process:
        mock_verse = VerseResult(
            topic="faith",
            verse_reference="Hebrews 11:1",
            verse_text="Now faith is confidence in what we hope for...",
            reflection="Faith is the foundation of our relationship with God.",
            timestamp=1735148400.0
        )
        mock_process.return_value = mock_verse

        response = await client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "456",
            "method": "execute",
            "params": {
                "messages": [
                    {
                        "role": "user",
                        "parts": [{"kind": "text", "text": "Get a verse on faith"}]
                    }
                ],
                "contextId": "ctx-123",
                "taskId": "task-456"
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "456"
        assert "result" in data
        assert isinstance(data["result"], dict)
        assert data["result"]["contextId"] == "ctx-123"
        assert data["result"]["id"] == "task-456"
