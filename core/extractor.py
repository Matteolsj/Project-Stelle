from ollama import chat
from pydantic import BaseModel
from typing import Literal

MODEL = "gemma3:4b"

class Fact(BaseModel):
    type: Literal["fact", "preference"]
    content: str

class FactList(BaseModel):
    facts: list[Fact]

EXTRACTION_PROMPT = """Extract durable facts about the user from this message.

RULES:
- Only extract stable, personal information (name, job, studies, hobbies, preferences, important life details).
- Ignore small talk, questions, temporary states ("I'm tired today"), and anything about the assistant.
- If nothing to extract, return an empty list.
- Write the "content" in English, third person, starting with "User".

Examples:
- "Hi, my name is Alex" -> [{"type": "fact", "content": "User's name is Alex"}]
- "I love coffee!" -> [{"type": "preference", "content": "User loves coffee"}]
- "Can you help me?" -> []
"""

def extract_facts(user_message):
    try:
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": user_message},
            ],
            format=FactList.model_json_schema(),
            options={
                "temperature": 0
            }
        )
        parsed = FactList.model_validate_json(response["message"]["content"])
        return [fact.model_dump() for fact in parsed.facts]
    except Exception as e:
        print(f"[Extractor] Error: {e}")
        return []