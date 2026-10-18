from core.tts import clean_for_tts


def test_hmph():
    assert "Hmph" not in clean_for_tts("Hmph. Fine.")
    assert "Hmm" in clean_for_tts("Hmph. Fine.")


def test_tch():
    assert "Tch" not in clean_for_tts("Tch. Whatever.")
    assert "Tsk" in clean_for_tts("Tch. Whatever.")


def test_hesitation_removed():
    assert "W-What" not in clean_for_tts("W-What?!")
    assert "What" in clean_for_tts("W-What?!")


def test_multiple_dots():
    assert "......" not in clean_for_tts("Wait...... what?")


def test_extra_spaces():
    assert "  " not in clean_for_tts("Hello    world")


def test_empty():
    assert clean_for_tts("") == ""