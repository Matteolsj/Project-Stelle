# Project Stelle

A tsundere AI companion running fully locally with Ollama, with persistent memory, emotion detection, text-to-speech, speech-to-text, and automatic fact extraction.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The Gemma 3 4B model:

```bash
ollama pull gemma3:4b
```

- whisper.cpp installed via Homebrew (for STT): 

```bash
brew install whisper-cpp
```

- A Piper voice model (downloaded separately, see below)

### Hardware

This project runs entirely on your machine. Here's what you need:

- **OS**: macOS Sonoma (14) or newer, or Linux/Windows (Ollama supports all three, but this project was tested on macOS).
- **RAM**: 8 GB is the absolute minimum for Gemma 3 4B, but **16 GB is strongly recommended** if you plan to use TTS and STT simultaneously. On 8 GB, you may experience slowdowns when all components are loaded at once.
- **Disk**: ~5 GB for the LLM, TTS voice, and Whisper model.
- **CPU/GPU**: Apple Silicon (M1/M2/M3/M4) is ideal. Intel Macs and Windows/Linux machines will work but will be slower (CPU-only inference for the LLM).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Voice Model

Download the Piper voice model (one time only):

```bash
python scripts/download_voice.py
```

This will download en_US-libritts_r-medium.onnx and its config file into voices/.

### Whisper Model

Download the whisper.cpp base.en model (one time only):

```bash
mkdir -p ~/Library/Application\ Support/whisper-cpp/models/
curl -L -o ~/Library/Application\ Support/whisper-cpp/models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

## Run

```bash
python main.py
```

Available commands in chat:

- `exit`: quit
- `reset`: clear both history and memories
- `reset history`: clear conversation history only
- `reset memory`: clear long-term memories only
- `mute`: disable text-to-speech
- `unmute`: re-enable text-to-speech
- `voice`: toggle voice input (press Enter without typing to speak)

## Structure

- `core/`: companion code
  - `brain.py`: orchestration (memory + history + LLM + parsing)
  - `conversation.py`: conversation history with disk persistence
  - `extractor.py`: automatic fact extraction from user messages
  - `llm.py`: wrapper around Ollama
  - `memory.py`: keyword-based long-term memory with deduplication
  - `parser.py`: parses the LLM's JSON output (reply + emotion + intensity)
  - `persona.py`: Stelle's personality and system prompt
  - `stt.py`: speech-to-text with whisper.cpp + Silero VAD
  - `tts.py`: Piper text-to-speech with cleanup for pronounceability
- `scripts/`:
  - `download_voice.py`: downloads the Piper voice model
- `data/`: runtime data (memories and history), created automatically on first run, not committed
- `voices/`: Piper voice models, not committed (downloaded via script)

## How it works

On each message:

1. The message is added to the conversation history
2. Relevant memories are retrieved by keyword matching
3. The system prompt, memories, and history are sent to the LLM
4. The LLM replies with JSON: {"reply": "...", "emotion": "...", "intensity": 0.0}
5. The response is parsed (with fallback for malformed JSON)
6. The reply is cleaned for text-to-speech and spoken aloud
7. Durable facts about the user are automatically extracted and stored
8. Everything is saved to disk

## Features

- Tsundere persona (Stelle) with 5 emotions: annoyed, smug, soft, surprised, happy
- Persistent memory: facts about the user are extracted automatically and stored
- Persistent history: conversations survive across sessions
- TTS: Piper, with cleanup for pronounceability
- STT: whisper.cpp + Silero VAD (voice activity detection)
- Fully local: Ollama, Piper, whisper.cpp, Silero VAD — no API calls, no cloud, no telemetry

## Known limitations

- Small model (Gemma 3 4B) means replies are sometimes short
- Contradictions between facts are partially handled (subject-based deduplication)
- Emotion classification is imperfect (~70% accuracy)
- Tested on MacBook Pro M1 (8 GB). On this hardware, running the LLM, TTS, and STT simultaneously can cause slowdowns. 16 GB is recommended for a smoother experience.
- Python 3.14 may show warnings from third-party libraries

## Roadmap

### Done
- [x] Text chat with tsundere persona
- [x] Persistent memory and conversation history
- [x] Emotion detection (5 emotions)
- [x] Local TTS with Piper
- [x] Local STT with whisper.cpp + Silero VAD
- [x] Automatic fact extraction

### In progress
- [ ] 2D avatar with emotion-based expressions

### Planned
- [ ] Improve contradiction handling in memory (give existing facts to the extractor)
- [ ] Smoother transitions between expressions (fade)
- [ ] Lip-sync with TTS audio
- [ ] Idle animations (blinking, breathing)
- [ ] Optional: Live2D support for richer avatars

### Known limitations to address
- [ ] Better emotion classification (currently ~70% accuracy)
- [ ] Longer, more nuanced replies (limited by the 4B model size)

## Credits

This project would not be possible without the following open-source tools and models:

- **Gemma 3** by Google — the language model running Stelle's personality. Subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
- **Ollama** — local LLM runtime.
- **Piper** by Michael Hansen — local text-to-speech synthesis (MIT License).
- **whisper.cpp** by Georgi Gerganov — local speech-to-text transcription (MIT License).
- **Silero VAD** — voice activity detection.
- **cascadevad-onnx** — ONNX runtime wrapper for Silero VAD.
- **PyQt6** — GUI framework (for the upcoming avatar).

## License

MIT. Feel free to clone, modify, and build your own waifu voice companion!