import pytest
from unittest.mock import patch, MagicMock
from bible_api import get_verse_by_topic, get_daily_verse

@patch('bible_api.requests.get')
def test_get_verse_by_topic_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "bookname": "John",
        "chapter": 3,
        "verse": 16,
        "text": "For God so loved the world..."
    }]
    mock_get.return_value = mock_response

    result = get_verse_by_topic("love")

    assert result.topic == "love"
    assert result.verse_reference == "John 3:16"
    assert result.verse_text == "For God so loved the world..."
    assert result.reflection is None

@patch('bible_api.requests.get')
def test_get_verse_by_topic_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        get_verse_by_topic("love")

@patch('bible_api.get_verse_by_topic')
def test_get_daily_verse(mock_get_verse):
    mock_verse = MagicMock()
    mock_get_verse.return_value = mock_verse

    result = get_daily_verse()

    assert result == mock_verse
    mock_get_verse.assert_called_once_with("daily")
