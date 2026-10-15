import json
import string
from pathlib import Path
from datetime import datetime
from unidecode import unidecode

BASE_DIR = Path(__file__).parents[1]
PATH = Path(BASE_DIR / "data" / "memories.json")
STOPWORDS = {
    "the", "a", "an", "in", "is", "to", "and", "i", "you", "it", "of", "for", "on", "with"
}

def load(path=PATH):
    if not path.exists():
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    
def save(path=PATH, content=None):
    if content is None:
        content = []
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def add(path=PATH, content=None, typeAdd: str = "fact"):
    data = load(path)
    if not isinstance(data, list):
        print("JSON root must be a list")
        return False
    new_memory = {
        "type": typeAdd,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    data.append(new_memory)
    save(path, data)
    return True

def delete_s(word):
    if word.endswith("s"):
        return word[:-1]
    return word

def clean(text):
    text = unidecode(text)
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def retrieve_memory(user_input, path=PATH):
    data = load(path)
    user_input_clean = clean(user_input)
    user_input_words = set(user_input_clean.split())
    user_input_words = {delete_s(word) for word in user_input_words if word not in STOPWORDS}
    res = []
    for memory in data:
        score = 0
        memory_clean = clean(memory["content"])
        memory_words = set(memory_clean.split())
        memory_words = {delete_s(word) for word in memory_words if word not in STOPWORDS}
        score = len(user_input_words & memory_words)
        if score > 0:
            res.append({
                "content": memory["content"],
                "score": score
            })
    res.sort(key=lambda x: x["score"], reverse=True)
    return res