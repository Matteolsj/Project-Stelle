import json
from unittest.mock import patch, MagicMock
from core.brain import brain
from core.conversation import Conversation

@patch("core.brain.ask_llm")
@patch("core.brain.extract_facts")
def test_brain_processes_valid_response(mock_extract, mock_ask_llm):
    mock_ask_llm.return_value = '{"reply": "Hmph. Fine.", "emotion": "annoyed", "intensity": 0.7}'
    mock_extract.return_value = []
    conversation = Conversation(load_disk=False)
    response = brain("Hello", conversation)
    assert response["reply"] == "Hmph. Fine."
    assert response["emotion"] == "annoyed"
    assert response["intensity"] == 0.7
    assert len(conversation.history) == 2
    assert conversation.history[0]["role"] == "user"
    assert conversation.history[1]["role"] == "assistant"

@patch("core.brain.ask_llm")
@patch("core.brain.extract_facts")
def test_brain_handles_malformed_json(mock_extract, mock_ask_llm):
    mock_ask_llm.return_value = "This is absolutely not a JSON!"
    mock_extract.return_value = []
    conversation = Conversation(load_disk=False)
    response = brain("Hello", conversation)
    assert "This is absolutely not a JSON!" in response["reply"]
    assert response["emotion"] == "annoyed"
    assert response["intensity"] == 0.5

@patch("core.brain.ask_llm")
@patch("core.brain.extract_facts")
@patch("core.brain.add_or_replace")
def test_brain_stores_extracted_facts(mock_add_or_replace, mock_extract, mock_ask_llm):
    mock_ask_llm.return_value = '{"reply": "Fine.", "emotion": "annoyed", "intensity": 0.5}'
    mock_extract.return_value = [
        {"type": "fact", "content": "User likes coffee"},
        {"type": "preference", "content": "User prefers short answers"},
    ]
    mock_add_or_replace.return_value = "added"
    conversation = Conversation(load_disk=False)
    brain("I like coffee", conversation)
    assert mock_add_or_replace.call_count == 2
    mock_add_or_replace.assert_any_call(content="User likes coffee", typeAdd="fact")
    mock_add_or_replace.assert_any_call(content="User prefers short answers", typeAdd="preference")

@patch("core.brain.ask_llm")
@patch("core.brain.extract_facts")
def test_brain_handles_extraction_error(mock_extract, mock_ask_llm):
    mock_ask_llm.return_value = '{"reply": "Fine.", "emotion": "annoyed", "intensity": 0.5}'
    mock_extract.side_effect = Exception("Extraction failed")
    conversation = Conversation(load_disk=False)
    response = brain("Hello", conversation)
    assert response["reply"] == "Fine."