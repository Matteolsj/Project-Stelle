from scripts.utils import download_file, get_whisper_model_path

WHISPER_REMOTE_NAME = "ggml-base.en.bin"
WHISPER_MODEL_PATH = get_whisper_model_path()
WHISPER_MODEL_DIR = WHISPER_MODEL_PATH.parent
WHISPER_HASH = "a03779c86df3323075f5e796cb2ce5029f00ec8869eee3fdfb897afe36c6d002"
WHISPER_URL = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/5359861c739e955e79d9a303bcbc70fb988958b1/{WHISPER_REMOTE_NAME}"

def main():
    WHISPER_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print("[download] Downloading Whisper base.en model (this may take a few minutes)...")
    dest = WHISPER_MODEL_PATH
    download_file(WHISPER_URL, dest, WHISPER_HASH)
    print(f"\nWhisper model is ready at: {dest}\n")

if __name__ == "__main__":
    main()