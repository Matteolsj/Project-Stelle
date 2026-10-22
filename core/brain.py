from core.llm import ask_llm
from core.memory import retrieve_memory, add_or_replace
from core.conversation import Conversation
from core.parser import parse_response
from core.extractor import extract_facts

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
    messages.append({"role": "assistant", "content": "{"})
    raw = ask_llm(messages)
    if not raw.lstrip().startswith("{"):
        raw = "{" + raw    
    parsed = parse_response(raw)
    conversation.add_assistant(
        parsed["reply"],
        parsed["emotion"],
        parsed["intensity"])
    conversation.trim()
    conversation.save()
    try:
        facts = extract_facts(user_input)
        for fact in facts:
            res = add_or_replace(content=fact["content"], typeAdd=fact["type"])
            if res == "added":
                print(f"[Memory] Learned: {fact['content']}")
            elif res == "replaced":
                print(f"[Memory] Updated: {fact['content']}")
    except Exception as e:
        print(f"[Memory] Extraction error: {e}")
    return parsed