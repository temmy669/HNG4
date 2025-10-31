import pytest
from unittest.mock import patch, MagicMock
from ai_service import extract_topic, generate_reflection, process_verse_request
from core.models import VerseResult

@patch('ai_service.model.generate_content')
def test_extract_topic(mock_generate):
    mock_response = MagicMock()
    mock_response.text = "love"
    mock_generate.return_value = mock_response

    topic = extract_topic("Get a verse on love")
    assert topic == "love"
    mock_generate.assert_called_once()

@patch('ai_service.model.generate_content')
def test_generate_reflection(mock_generate):
    mock_response = MagicMock()
    mock_response.text = "This verse emphasizes the importance of love."
    mock_generate.return_value = mock_response

    reflection = generate_reflection("God is love.", "love")
    assert reflection == "This verse emphasizes the importance of love."
    mock_generate.assert_called_once()

@patch('ai_service.extract_topic')
@patch('ai_service.generate_reflection')
@patch('ai_service.get_verse_by_topic')
def test_process_verse_request(mock_get_verse, mock_gen_reflect, mock_extract):
    mock_extract.return_value = "love"
    mock_verse = VerseResult(
        topic="love",
        verse_reference="1 John 4:8",
        verse_text="Whoever does not love does not know God, because God is love.",
        timestamp=1735148400.0
    )
    mock_get_verse.return_value = mock_verse
    mock_gen_reflect.return_value = "Reflection text."

    result = process_verse_request("Get a verse on love")

    assert result.topic == "love"
    assert result.verse_reference == "1 John 4:8"
    assert result.reflection == "Reflection text."
    mock_extract.assert_called_once_with("Get a verse on love")
    mock_get_verse.assert_called_once_with("love")
    mock_gen_reflect.assert_called_once_with("Whoever does not love does not know God, because God is love.", "love")

@patch('ai_service.model.generate_content', side_effect=Exception("API error"))
def test_extract_topic_failure(mock_generate):
    with pytest.raises(Exception):
        extract_topic("love")

@patch('ai_service.model.generate_content', side_effect=Exception("API error"))
def test_generate_reflection_failure(mock_generate):
    with pytest.raises(Exception):
        generate_reflection("text", "topic")
