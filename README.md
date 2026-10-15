# Project Stelle

A tsundere AI companion running locally with Ollama.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The Gemma 3 4B model:

```bash
ollama pull gemma3:4b
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Available commands in chat:

- `exit`: quit
- `reset`: clear conversation history

## Structure

- `core/`: companion code
  - `brain.py`: orchestration (memory + history + LLM)
  - `conversation.py`: conversation history with disk persistence
  - `llm.py`: wrapper around Ollama
  - `memory.py`: keyword-based long-term memory
  - `persona.py`: Stelle's personality
- `data/`: runtime data (memories and history), created automatically on first run, never committed

## How it works

On each message:

1. The message is added to the conversation history
2. Relevant memories are retrieved by keyword matching
3. Everything is sent to the LLM (Gemma 3 4B via Ollama)
4. The response is cleaned (no Markdown), added to history, and saved to disk