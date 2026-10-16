import json
import re

VALID_EMOTIONS = {"annoyed", "smug", "soft", "surprised", "happy"}

def parse_response(raw):
    fallback = {
        "reply": raw.strip() if raw else "",
        "emotion": "annoyed",
        "intensity": 0.5,
    }
    if not raw:
        return fallback
    cleaned = raw.strip()
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
    cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return fallback
    
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return fallback
    
    reply = data.get("reply")
    emotion = data.get("emotion")
    intensity = data.get("intensity", 0.5)

    if not isinstance(reply, str) or not reply.strip():
        return fallback

    if emotion not in VALID_EMOTIONS:
        emotion = "annoyed"

    try:
        intensity = float(intensity)
        intensity = max(0.0, min(1.0, intensity))
    except (ValueError, TypeError):
        intensity = 0.5

    reply = re.sub(r"\*\*([^*]+)\*\*", r"\1", reply)
    reply = re.sub(r"\*([^*]+)\*", r"\1", reply)

    return {
        "reply": reply.strip(),
        "emotion": emotion,
        "intensity": intensity,
    }