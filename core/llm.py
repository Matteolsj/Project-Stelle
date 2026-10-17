from ollama import chat

MODEL = "gemma3:4b"

def ask_llm(messages):
    response = chat(
        model=MODEL,
        messages=messages,
        think=False,
	options={
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.2
            }
        )
    return response["message"]["content"]
