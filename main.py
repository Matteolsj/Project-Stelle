from core.brain import brain
from core.persona import PERSONA
from core.conversation import Conversation

def main():
    conversation = Conversation()
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
        response = brain(user_input, conversation)
        print(f"{PERSONA["name"]}:", response)

if __name__ == "__main__":
    main()