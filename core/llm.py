from ollama import chat

#MODEL = "llama3"
#MODEL = "mistral"
MODEL = "phi3"

def ask_llm(messages):
    response = chat(
        model=MODEL,
        messages=messages
    )
    return response["message"]["content"]