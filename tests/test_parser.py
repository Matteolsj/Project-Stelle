from core.parser import parse_response


def test_valid_json():
    raw = '{"reply": "Fine.", "emotion": "annoyed", "intensity": 0.7}'
    result = parse_response(raw)
    assert result["reply"] == "Fine."
    assert result["emotion"] == "annoyed"
    assert result["intensity"] == 0.7


def test_curly_quotes():
    raw = '{“reply”: “Fine.”, “emotion”: “annoyed”, “intensity”: 0.7}'
    result = parse_response(raw)
    assert result["reply"] == "Fine."
    assert result["emotion"] == "annoyed"


def test_markdown_wrapped():
    raw = '```json\n{"reply": "Hi", "emotion": "soft", "intensity": 0.5}\n```'
    result = parse_response(raw)
    assert result["reply"] == "Hi"
    assert result["emotion"] == "soft"


def test_asterisks_removed():
    raw = '{"reply": "You *really* needed that?", "emotion": "annoyed", "intensity": 0.5}'
    result = parse_response(raw)
    assert "*" not in result["reply"]
    assert "really" in result["reply"]


def test_invalid_emotion_fallback():
    raw = '{"reply": "Hi", "emotion": "banana", "intensity": 0.5}'
    result = parse_response(raw)
    assert result["emotion"] == "annoyed"


def test_intensity_clamped():
    raw = '{"reply": "Hi", "emotion": "annoyed", "intensity": 5.0}'
    result = parse_response(raw)
    assert 0.0 <= result["intensity"] <= 1.0


def test_completely_broken_fallback():
    raw = "anything anywhere testing this!!!???"
    result = parse_response(raw)
    assert result["reply"] == "anything anywhere testing this!!!???"
    assert result["emotion"] == "annoyed"
    assert result["intensity"] == 0.5


def test_empty_input():
    result = parse_response("")
    assert result["reply"] == ""
    assert result["emotion"] == "annoyed"