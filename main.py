from core.brain import brain

def main():
    print("AI ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = brain(user_input)
        print("AI:", response)

if __name__ == "__main__":
    main()