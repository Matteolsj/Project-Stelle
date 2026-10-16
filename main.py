from core.brain import brain
from core.persona import PERSONA
from core.conversation import Conversation
from core.tts import TTS

def main():
    conversation = Conversation()
    tts = TTS()
    tts_enabled = True
    print("AI ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "reset":
            conversation.reset()
            print("(history cleared)")
            continue
        if user_input.lower() == "mute":
            tts_enabled = False
            print("(muted)")
            continue
        if user_input.lower() == "unmute":
            tts_enabled = True
            print("(unmuted)")
            continue
        response = brain(user_input, conversation)
        print(f"{PERSONA['name']}: {response['reply']}")
        print(f"[{response['emotion']} | {response['intensity']:.1f}]")
        if tts_enabled:
            tts.speak(response["reply"])

if __name__ == "__main__":
    main()