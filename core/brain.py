from core.persona import get_system_prompt
from core.llm import ask_llm
from core.memory import retrieve_memory
from core.persona import get_system_prompt

def chat(user_input):
    system_prompt = get_system_prompt()
    messages = [
        {"role" : "system", "content" : system_prompt},
        {"role" : "user", "content" : user_input}
        ]
    response = ask_llm(messages)
    return response

def format_memories(memories):
    res = """User memories:"""
    for item in memories:
        res += f"\n - {item["content"]}"
    return res

def build_prompt(user_input, memory_context):
    res = f"""{get_system_prompt()}\n{memory_context}\n\nUser Input:\n{user_input}"""
    return res

def brain(user_input):
    memories = retrieve_memory(user_input)
    memory_context = format_memories(memories)
    prompt = build_prompt(user_input, memory_context)
    response = chat(prompt)
    return response