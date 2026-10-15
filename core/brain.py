from core.persona import get_system_prompt
from core.llm import ask_llm
from core.memory import retrieve_memory
from core.conversation import Conversation
import re

def clean_response(text):
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # **gras**
    text = re.sub(r"\*([^*]+)\*", r"\1", text)      # *italique*
    return text

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
    response = ask_llm(messages)
    response = clean_response(response)
    conversation.add_assistant(response)
    conversation.trim()
    conversation.save()
    return response