import re
import wave
import tempfile
import subprocess
from pathlib import Path
from piper import PiperVoice, SynthesisConfig

VOICE_PATH = Path(__file__).parents[1] / "voices" / "en_US-libritts_r-medium.onnx"

SPEAKER_ID = 0
LENGTH_SCALE = 1.1
NOISE_SCALE = 0.667
NOISE_W_SCALE = 0.8

def clean_for_tts(text):
    text = re.sub(r"\bHmph\b", "Hmm", text, flags=re.IGNORECASE)
    text = re.sub(r"\bTch\b", "Tsk", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\w-(\w+)\b", r"\1", text)
    text = re.sub(r"\.{4,}", "...", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

class TTS:
    def __init__(self, voice_path=VOICE_PATH):
        self.voice_path = Path(voice_path)
        if not self.voice_path.exists():
            raise FileNotFoundError(f"Voice model not found: {self.voice_path}")
        print(f"[TTS] Loading voice: {self.voice_path.name}")
        self.voice = PiperVoice.load(str(self.voice_path))
        self.syn_config = SynthesisConfig(
            speaker_id=SPEAKER_ID,
            length_scale=LENGTH_SCALE,
            noise_scale=NOISE_SCALE,
            noise_w_scale=NOISE_W_SCALE,
        )
        print("[TTS] Voice loaded.")

    def speak(self, text):
        if not text or not text.strip():
            return
        cleaned = clean_for_tts(text)
        if not cleaned:
            return
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with wave.open(tmp_path, "wb") as wav_file:
                self.voice.synthesize_wav(cleaned, wav_file, syn_config=self.syn_config)
            subprocess.run(["afplay", tmp_path], check=False)
        finally:
            Path(tmp_path).unlink(missing_ok=True)