from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import asyncio
import re
import threading
from core.brain import brain
from core.conversation import Conversation
from core.tts import TTS
from core.memory import reset_memory
from core.stt import STT

WEB_DIR = Path(__file__).parent / "web"
WEB_DIR.mkdir(exist_ok=True)
ALLOWED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

app = FastAPI()
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

conversation = Conversation()
executor = ThreadPoolExecutor(max_workers=2)
conversation_lock = asyncio.Lock()
init_lock = threading.Lock()

tts_instance = None
stt_instance = None

def get_tts():
    global tts_instance
    if tts_instance is not None:
        return tts_instance
    with init_lock:
        if tts_instance is None:
            try:
                tts_instance = TTS()
            except FileNotFoundError as e:
                print(f"[TTS] Warning: Cannot load voice model: {e}")
                print("[TTS] Text chat will work, but audio output is disabled.")
                return None
        return tts_instance

def get_stt():
    global stt_instance
    if stt_instance is not None:
        return stt_instance
    with init_lock:
        if stt_instance is None:
            try:
                stt_instance = STT()
            except Exception as e:
                print(f"[STT] Warning: Cannot load STT: {e}")
                print("[STT] Voice input is disabled.")
                return None
        return stt_instance

def generate_audio(text):
    tts = get_tts()
    if tts is None:
        return None
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        tmp.close()
    try:
        tts.synthesize_to_file(text, tmp_path)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)

@app.get("/")
async def get():
    html_file = WEB_DIR / "index.html"
    if html_file.exists():
        return HTMLResponse(html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Page not found. Create web/index.html</h1>")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        print(f"[WS] Connection refused from unauthorized origin: {origin}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    print("[WS] Client connected")
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            data = await websocket.receive()

            if "text" in data:
                text_data = data["text"]
                print(f"[WS] Received text: {text_data}")

                try:
                    cmd = json.loads(text_data)
                    if isinstance(cmd, dict) and cmd.get("command") == "reset":
                        async with conversation_lock:
                            conversation.reset()
                            reset_memory()
                        print("[WS] Reset done")
                        await websocket.send_text(json.dumps({
                            "reply": "(history and memories cleared)",
                            "emotion": "annoyed",
                            "intensity": 0.3,
                        }))
                        continue
                except json.JSONDecodeError:
                    pass

                async with conversation_lock:
                    response = await loop.run_in_executor(executor, brain, text_data, conversation)

                await websocket.send_text(json.dumps({
                    "reply": response["reply"],
                    "emotion": response["emotion"],
                    "intensity": response["intensity"],
                }))
                
                audio_bytes = await loop.run_in_executor(executor, generate_audio, response["reply"])
                if audio_bytes:
                    await websocket.send_bytes(audio_bytes)

            elif "bytes" in data:
                stt = await loop.run_in_executor(executor, get_stt)
                if stt is None:
                    await websocket.send_text(json.dumps({
                        "reply": "(Voice input is not available. Please install the Whisper model.)",
                        "emotion": "annoyed",
                        "intensity": 0.3,
                    }))
                    continue
                audio_data = data["bytes"]
                print(f"[WS] Received audio: {len(audio_data)} bytes")

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    wav_path = Path(tmp.name)

                try:
                    transcribed_text = await loop.run_in_executor(executor, stt.transcribe, str(wav_path))
                    print(f"[STT] Raw transcribed: {transcribed_text}")

                    cleaned_text = re.sub(r'\[.*?\]|\(.*?\)|\*.*?\*', '', transcribed_text).strip().strip('"').strip("'").replace("Stell", "Stelle")

                    if not cleaned_text:
                        print("[STT] Ignoring noise tag.")
                        await websocket.send_text(json.dumps({
                            "reply": "(I didn't hear anything clear)",
                            "emotion": "annoyed",
                            "intensity": 0.3,
                        }))
                        continue

                    await websocket.send_text(json.dumps({"transcription": cleaned_text}))

                    async with conversation_lock:
                        response = await loop.run_in_executor(executor, brain, cleaned_text, conversation)
                    
                    await websocket.send_text(json.dumps({
                        "reply": response["reply"],
                        "emotion": response["emotion"],
                        "intensity": response["intensity"],
                    }))
                    
                    audio_bytes = await loop.run_in_executor(executor, generate_audio, response["reply"])
                    if audio_bytes:
                        await websocket.send_bytes(audio_bytes)
                finally:
                    wav_path.unlink(missing_ok=True)

        except RuntimeError:
            print("[WS] Server shutting down, closing connection.")
            break
        except WebSocketDisconnect:
            print("[WS] Client disconnected")
            break
        except Exception as e:
            print(f"[WS] Error: {e}")
            break