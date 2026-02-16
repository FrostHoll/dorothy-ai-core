from app.domain.entities.message import Message


def msg_to_llama_format(message: Message):
    return {"role": message.role, "content": message.content}


def msg_list_to_llama_format(messages: list[Message]):
    return [
        {"role": m.role, "content": m.content}
        for m in messages
    ]


def llama_format_to_msg(message_obj) -> Message:
    return Message(role=message_obj["role"], content=message_obj["content"])


def wrap_text_to_llama_format(role: str, text: str):
    return {"role": role, "content": text}