import json
from pathlib import Path
from datetime import datetime
from core.persona import get_system_prompt

MAX_TURNS = 10
HISTORY_PATH = Path(__file__).parents[1]/"data"/"history.json"

class Conversation:
    def __init__(self, load_disk=True):
        self.system_prompt = get_system_prompt()
        self. history = []
        if load_disk:
            self._load()

    def add_user(self, content):
        self.history.append({
            "role" : "user",
            "content" : content,
            "timestamp" : datetime.now().isoformat()
        })

    def add_assistant(self, content):
        self.history.append({
            "role" : "assistant",
            "content" : content,
            "timestamp" : datetime.now().isoformat()
        })

    def trim(self):
        max_messages = 2 * MAX_TURNS
        if len(self.history)>max_messages:
            self.history = self.history[-max_messages:]

    def build_message(self, memory_context=""):
        messages = [{"role": "system", "content": self.system_prompt}]
        if memory_context:
            messages.append({"role": "system", "content": memory_context})
        for message in self.history:
            messages.append({"role": message["role"], "content": message["content"]})
        return messages

    def reset(self):
        self.history = []
        self.save()

    def _load(self):
        if not HISTORY_PATH.exists():
            return
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.history = data.get("history", [])
        except (json.JSONDecodeError, KeyError):
            self.history = []

    def save(self):
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump({"history" : self.history}, f, ensure_ascii=False, indent=2)

    