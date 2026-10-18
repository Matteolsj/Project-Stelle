from core.brain import brain
from core.persona import PERSONA
from core.memory import reset_memory
from core.conversation import Conversation
from core.tts import TTS
from core.stt import STT
import subprocess
import sys
from pathlib import Path

avatar_script = Path(__file__).parent / "core" / "avatar.py"
avatar_process = subprocess.Popen([sys.executable, str(avatar_script)])

def main():
    conversation = Conversation()
    tts = TTS()
    stt = STT()
    tts_enabled = False
    voice_mode = False
    print("AI ready.")
    print("Commands: reset, reset history, reset memory, mute, unmute, voice (toggle voice input)")
    print("Type 'exit' to quit.")
    while True:
        if voice_mode:
            user_input = input("You [voice] (press Enter to speak): ").strip()
            if not user_input:
                try:
                    user_input = stt.listen()
                    print(f"You said: {user_input}")
                except Exception as e:
                    print(f"[STT error] {e}")
                    continue
                if not user_input:
                    print("(no speech detected)")
                    continue
        else:
            user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            avatar_process.terminate()
            break
        if user_input.lower() == "reset history":
            conversation.reset()
            print("(history cleared)")
            continue
        if user_input.lower() == "reset memory":
            reset_memory()
            print("(memories cleared)")
            continue
        if user_input.lower() == "reset":
            conversation.reset()
            reset_memory()
            print("(history and memories cleared)")
            continue
        if user_input.lower() == "mute":
            tts_enabled = False
            print("(muted)")
            continue
        if user_input.lower() == "unmute":
            tts_enabled = True
            print("(unmuted)")
            continue
        if user_input.lower() == "voice":
            voice_mode = not voice_mode
            state = "on" if voice_mode else "off"
            print(f"(voice input {state})")
            continue
        response = brain(user_input, conversation)
        print(f"{PERSONA['name']}: {response['reply']}")
        print(f"[{response['emotion']} | {response['intensity']:.1f}]")
        if tts_enabled:
            tts.speak(response["reply"])

if __name__ == "__main__":
    main()