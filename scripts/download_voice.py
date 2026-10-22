from pathlib import Path
from utils import download_file

VOICES_DIR = Path(__file__).parents[1] / "voices"

VOICE_NAME = "en_US-libritts_r-medium"
BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/5041a7a49ae5b3a0f30e6837769eb03fdbb231bd/en/en_US/libritts_r/medium"

FILES = [
    (f"{VOICE_NAME}.onnx", f"{BASE_URL}/{VOICE_NAME}.onnx", "10bb85e071d616fcf4071f369f1799d0491492ab3c5d552ec19fb548fac13195"),
    (f"{VOICE_NAME}.onnx.json", f"{BASE_URL}/{VOICE_NAME}.onnx.json", "b471dc60d2d8335e819c393d196d6fbf792817f40051257b269878505bc9afb3")
]

def main():
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    print("[download] This may take a few minutes depending on your connection.")
    for filename, url, expected_hash in FILES:
        dest = VOICES_DIR / filename
        download_file(url, dest, expected_hash)
    print("\nAll voice files are ready in voices/\n")

if __name__ == "__main__":
    main()