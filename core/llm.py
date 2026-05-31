from ollama import chat

#MODEL = "llama3"
MODEL = "mistral"
#MODEL = "phi3"

def ask_llm(messages):
    response = chat(
        model=MODEL,
        messages=messages,
        options={
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1
            }
        )
    return response["message"]["content"]