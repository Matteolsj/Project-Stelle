import os
import tempfile
import time
import subprocess
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
from cascadevad import load_vad

SAMPLE_RATE = 16000
CHANNELS = 1
WHISPER_MODEL = os.path.expanduser("~/Library/Application Support/whisper-cpp/models/ggml-base.en.bin")

VAD_THRESHOLD = 0.5
MIN_SILENCE_MS = 700
MAX_RECORD_SECONDS = 30
CHUNK_SIZE = 512
AMPLITUDE_THRESHOLD = 0.005

class STT:
    def __init__(self, model_path=WHISPER_MODEL):
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Whisper model not found: {model_path}")
        self.model_path = model_path
        print("[STT] Loading Silero VAD...")
        self.vad = load_vad()
        print("[STT] Silero VAD loaded.")

    def _is_speech(self, chunk):
        if np.abs(chunk).max()<AMPLITUDE_THRESHOLD:
            return False
        pcm_int16 = (chunk * 32767).astype(np.int16)
        prob = self.vad.process_chunk(pcm_int16)
        return prob > VAD_THRESHOLD

    def record_until_silence(self):
        print("[STT] Listening... speak now.")
        chunks = []
        speech_started = False
        silence_start = None
        start_time = time.time()

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            blocksize=CHUNK_SIZE,
        ) as stream:
            while True:
                chunk = stream.read(CHUNK_SIZE)[0]
                chunk = chunk[:, 0].copy()
                is_speech = self._is_speech(chunk)
                if is_speech:
                    if not speech_started:
                        speech_started = True
                        print("[STT] Speech detected.")
                    silence_start = None
                    chunks.append(chunk)
                else:
                    if speech_started:
                        chunks.append(chunk)
                        if silence_start is None:
                            silence_start = time.time()
                        elif (time.time() - silence_start) > (MIN_SILENCE_MS / 1000.0):
                            break
                if (time.time() - start_time) > MAX_RECORD_SECONDS:
                    print("[STT] Max duration reached.")
                    break
        if not chunks:
            print("[STT] No speech detected.")
            return None
        
        audio = np.concatenate(chunks)
        if np.abs(audio).max() < 0.01:
            print("[STT] Signal too weak.")
            return None

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()
        sf.write(tmp_path, audio, SAMPLE_RATE)
        return tmp_path
            

    def transcribe(self, wav_path):
        output_prefix = wav_path.replace(".wav", "_out")
        cmd = [
            "whisper-cli",
            "-m", self.model_path,
            "-f", wav_path,
            "-otxt",
            "-of", output_prefix,
            "--no-prints"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        txt_path = output_prefix + ".txt"
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
        finally:
            Path(txt_path).unlink(missing_ok=True)
        return text

    def listen(self):
        wav_path = self.record_until_silence()
        if wav_path is None:
            return ""
        try:
            text = self.transcribe(wav_path)
        finally:
            Path(wav_path).unlink(missing_ok=True)
        return text