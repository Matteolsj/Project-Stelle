from scripts.download_voice import main as download_voice
from scripts.download_vad import main as download_vad
from scripts.download_whisper import main as download_whisper

def main():
    print("Downloading all Stelle models")

    print("\n--- Piper Voice Model ---")
    download_voice()

    print("\n--- VAD Files ---")
    download_vad()

    print("\n--- Whisper Model ---")
    download_whisper()

    print("All models are ready!")

if __name__ == "__main__":
    main()