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
VERBS = {
    "likes", "liked", "loves", "loved", "prefers", "preferred",
    "is", "was", "has", "had", "does", "did",
    "drinks", "drank", "eats", "ate",
    "studies", "studied", "works", "worked",
    "plays", "played", "codes", "coded",
    "builds", "built", "enjoys", "enjoyed",
    "user", "users", "no", "not", "longer",
    "anymore", "never", "doesn't", "don't",
    "didn't", "isn't", "wasn't", "won't", "can't", "cannot",
}

class MemoryCorruptedError(Exception):
    pass

def load(path=PATH):
    if not path.exists():
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Memory] Error : File {path} is corrupted.")
        backup_path = path.with_suffix(".json.corrupt")
        import shutil
        shutil.copy(path, backup_path)
        print(f"[Memory] Backup copy has been created : {backup_path}")
        raise MemoryCorruptedError(f"File {path} is not readable.")
    
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

def reset_memory(path=PATH):
    save(path, [])

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
    try:
        data = load(path)
    except MemoryCorruptedError:
        print("[Memory] Warning: memories.json is corrupted, ignoring memories for this message.")
        return []
    if not isinstance(data, list):
        print("[Memory] Warning: memories.json root is not a list, ignoring memories.")
        return []
    user_input_clean = clean(user_input)
    user_input_words = set(user_input_clean.split())
    user_input_words = {delete_s(word) for word in user_input_words if word not in STOPWORDS}
    res = []
    for memory in data:
        if not isinstance(memory, dict):
            continue
        content = memory.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
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

def extract_subject(content):
    words = clean(content).split()
    return {w for w in words if w not in VERBS and w not in STOPWORDS}

def find_similar_fact(content, data=None, path=PATH):
    if data is None:
        data = load(path)
    target_subject = extract_subject(content)
    if not target_subject:
        return -1
    for i, memory in enumerate(data):
        if not isinstance(memory, dict):
            continue
        existing_content = memory.get("content")
        if not isinstance(existing_content, str) or not existing_content.strip():
            continue
        existing_subject = extract_subject(existing_content)
        if not existing_subject:
            continue
        common = target_subject & existing_subject
        if target_subject == existing_subject or len(common) >= 2:
            return i
    return -1

def add_or_replace(content, typeAdd="fact", path=PATH):
    try:
        data = load(path)
    except MemoryCorruptedError:
        print("[Memory] Skipped to avoid losing data.")
        return "skipped"
    if not isinstance(data, list):
        print("JSON root must be a list")
        return "skipped"
    
    index = find_similar_fact(content, data=data, path=path)
    if index>=0:
        data[index] = {
            "type": typeAdd,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        save(path, data)
        return "replaced"
    data.append({
        "type": typeAdd,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    })
    save(path, data)
    return "added"