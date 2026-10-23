import json
import re
import unicodedata

VALID_EMOTIONS = {"annoyed", "smug", "soft", "surprised", "sad"}

def parse_response(raw):
    if not raw:
        return {"reply": "", "emotion": "annoyed", "intensity": 0.5}

    cleaned = raw.strip()
    cleaned = unicodedata.normalize("NFKC", cleaned)
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
    cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = cleaned.replace("，", ",")
    cleaned = cleaned.replace("：", ":")
    cleaned = cleaned.replace("｛", "{").replace("｝", "}")
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    data = None
    if match:
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            data = None

    if not isinstance(data, dict):
        data = {
            "reply": cleaned,
            "emotion": "annoyed",
            "intensity": 0.5,
        }

    reply = data.get("reply", "")
    emotion = data.get("emotion", "annoyed")
    intensity = data.get("intensity", 0.5)

    if isinstance(reply, str):
        reply = re.sub(r"\*\*([^*]+)\*\*", r"\1", reply)
        reply = re.sub(r"\*([^*]+)\*", r"\1", reply)
        reply = reply.strip()
    else:
        reply = ""

    if not reply:
        return {"reply": "", "emotion": "annoyed", "intensity": 0.5}

    if emotion not in VALID_EMOTIONS:
        emotion = "annoyed"

    try:
        intensity = float(intensity)
        intensity = max(0.0, min(1.0, intensity))
    except (ValueError, TypeError):
        intensity = 0.5

    return {
        "reply": reply,
        "emotion": emotion,
        "intensity": intensity,
    }