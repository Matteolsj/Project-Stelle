import sys
from pathlib import Path
from urllib.request import urlretrieve

VOICE_NAME = "en_US-libritts_r-medium"
BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium"

FILES = [
    f"{VOICE_NAME}.onnx",
    f"{VOICE_NAME}.onnx.json",
]

VOICES_DIR = Path(__file__).parents[1] / "voices"

def download_file(url, dest, filename):
    if dest.exists():
        print(f"[skip] {filename} already exists.")
        return
    print(f"[download] {filename} ...")
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        urlretrieve(url, tmp)
        tmp.rename(dest)
        print(f"[done] {filename} ({dest.stat().st_size//1024//1024} MB)")
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        print(f"[error] Failed to download {filename}: {e}")
        sys.exit(1)

def main():
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    print("[download] This may take a few minutes depending on your connection.")
    for filename in FILES:
        url = f"{BASE_URL}/{filename}"
        dest = VOICES_DIR / filename
        download_file(url, dest, filename)
    print("\nAll voice files are ready in voices/\n")

if __name__ == "__main__":
    main()
