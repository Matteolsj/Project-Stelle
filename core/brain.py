from core.persona import get_system_prompt
from core.llm import ask_llm
from core.memory import retrieve_memory
from core.conversation import Conversation
from core.parser import parse_response

def format_memories(memories, max_items=5):
    if not memories:
        return ""
    top = memories[:max_items]
    res = "\n".join(f"- {item['content']}" for item in top)
    return f"Things you remember about the user:\n{res}"

def brain(user_input, conversation: Conversation):
    conversation.add_user(user_input)
    memories = retrieve_memory(user_input)
    memory_context = format_memories(memories)
    messages = conversation.build_message(memory_context)
    raw = ask_llm(messages)
    parsed = parse_response(raw)
    conversation.add_assistant(
        parsed["reply"],
        parsed["emotion"],
        parsed["intensity"])
    conversation.trim()
    conversation.save()
    return parsed