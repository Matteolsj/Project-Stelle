from ollama import chat

#MODEL = "llama3"
#MODEL = "mistral"
#MODEL = "phi3"
#MODEL = "qwen3:0.6b"
#MODEL = "qwen3:1.7b"
#MODEL = "qwen3:4b"
MODEL = "gemma3:4b"

def ask_llm(messages):
    response = chat(
        model=MODEL,
        messages=messages,
        #think=False,
	options={
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.2
            }
        )
    return response["message"]["content"]
