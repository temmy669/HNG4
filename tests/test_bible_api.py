import pytest
from unittest.mock import patch, MagicMock
from core.bible_api import get_verse_by_topic, get_daily_verse

@patch('core.bible_api.requests.get')
@patch('core.bible_api.generate_verse_reference')
def test_get_verse_by_topic_success(mock_generate, mock_get):
    mock_generate.return_value = "John 3:16"
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

@patch('core.bible_api.requests.get')
@patch('core.bible_api.generate_verse_reference')
def test_get_verse_by_topic_fallback(mock_generate, mock_get):
    mock_generate.side_effect = Exception("AI failed")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "bookname": "Genesis",
        "chapter": 1,
        "verse": 1,
        "text": "In the beginning..."
    }]
    mock_get.return_value = mock_response

    result = get_verse_by_topic("creation")

    assert result.topic == "creation"
    assert result.verse_reference == "Genesis 1:1"
    assert result.verse_text == "In the beginning..."
    assert result.reflection is None

@patch('core.bible_api.get_random_verse')
@patch('core.bible_api.generate_verse_reference')
def test_get_verse_by_topic_api_failure(mock_generate, mock_get_random):
    mock_generate.return_value = "Invalid Reference"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get_random.return_value = MagicMock()

    result = get_verse_by_topic("love")

    mock_get_random.assert_called_once_with("love")

@patch('core.bible_api.get_verse_by_topic')
def test_get_daily_verse(mock_get_verse):
    mock_verse = MagicMock()
    mock_get_verse.return_value = mock_verse

    result = get_daily_verse()

    assert result == mock_verse
    mock_get_verse.assert_called_once_with("daily")
