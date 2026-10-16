# Project Stelle

A tsundere AI companion running locally with Ollama, with persistent memory,
emotion detection, and text-to-speech.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The Gemma 3 4B model:

```bash
ollama pull gemma3:4b
```

- A Piper voice model (downloaded separately, see below)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Voice Model

Download a Piper voice and place both files in voices/:

- en_US-libritts_r-medium.onnx
- en_US-libritts_r-medium.onnx.json
Available at: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/libritts_r/medium

## Run

```bash
python main.py
```

Available commands in chat:

- `exit`: quit
- `reset`: clear conversation history
- `mute`: disable text-to-speech
- `unmute`: re-enable text-to-speech

## Structure

- `core/`: companion code
  - `brain.py`: orchestration (memory + history + LLM + parsing)
  - `conversation.py`: conversation history with disk persistence
  - `llm.py`: wrapper around Ollama
  - `memory.py`: keyword-based long-term memory
  - `persona.py`: Stelle's personality and system prompt
  - `parser.py`: parses the LLM's JSON output (reply + emotion + intensity)
  - `tts.py`: Piper text-to-speech with cleanup for pronounceability
- `data/`: runtime data (memories and history), created automatically on first run, never committed
- `voice/`: Piper voice models, not committed

## How it works

On each message:

1. The message is added to the conversation history
2. Relevant memories are retrieved by keyword matching
3. The system prompt, memories, and history are sent to the LLM
4. The LLM replies with JSON: {"reply": "...", "emotion": "...", "intensity": 0.0}
5. The response is parsed (with fallback for malformed JSON)
6. The reply is cleaned for text-to-speech and spoken aloud
7. Everything is saved to disk