from core.memory import clean, extract_subject, add_or_replace, find_similar_fact, load, save


def test_clean():
    assert clean("User likes Coffee!") == "user likes coffee"
    assert clean("Stùdÿîng Cômpùtèr Scìêncë.") == "studying computer science"


def test_extract_subject():
    assert extract_subject("User loves coffee") == {"coffee"}
    assert extract_subject("User is French") == {"french"}
    assert "user" not in extract_subject("User likes Python")


def test_add_then_replace(tmp_path):
    path = tmp_path / "memories.json"
    save(path, [])

    result = add_or_replace("User loves coffee", path=path)
    assert result == "added"
    assert len(load(path)) == 1

    result = add_or_replace("User no longer likes coffee", path=path)
    assert result == "replaced"
    memories = load(path)
    assert len(memories) == 1
    assert "no longer" in memories[0]["content"]


def test_add_different_subject(tmp_path):
    path = tmp_path / "memories.json"
    save(path, [])

    add_or_replace("User loves coffee", path=path)
    add_or_replace("User studies computer science", path=path)
    assert len(load(path)) == 2


def test_find_similar_fact(tmp_path):
    path = tmp_path / "memories.json"
    save(path, [
        {"type": "fact", "content": "User loves coffee", "timestamp": "2026-01-01"},
    ])

    assert find_similar_fact("User no longer likes coffee", path=path) == 0
    assert find_similar_fact("User plays guitar", path=path) == -1