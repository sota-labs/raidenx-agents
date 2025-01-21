import json
import os
from typing import List

from llama_index.core.llms import ChatMessage, MessageRole

HISTORY_FILE = "chat_history.json"


def load_chat_history():
    try:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
    except json.JSONDecodeError:
        print(f"Lỗi khi đọc file {HISTORY_FILE}. Tạo file mới.")
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def save_chat_history(history):
    """Lưu lịch sử chat vào file JSON"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def convert_dict_to_chat_messages(
    chat_dicts: List[dict[str, str]],
) -> List[ChatMessage]:
    """
    Convert a list of dictionaries to a list of ChatMessage objects.

    Args:
        chat_dicts (List[Dict[str, str]]): A list of dictionaries with "role" and "content" keys.

    Returns:
        List[ChatMessage]: A list of ChatMessage objects.
    """
    chat_messages = []
    for chat_dict in chat_dicts:
        # Ensure the dictionary has the required keys
        if "role" not in chat_dict or "content" not in chat_dict:
            raise ValueError("Each dictionary must contain 'role' and 'content' keys.")

        # Normalize the role to match the MessageRole class
        role = chat_dict["role"].lower()
        if role not in [MessageRole.ASSISTANT, MessageRole.USER]:
            raise ValueError(
                f"Invalid role: {role}. Role must be 'assistant' or 'user'."
            )

        # Create a ChatMessage object and add it to the list
        chat_message = ChatMessage(role=role, content=chat_dict["content"])
        chat_messages.append(chat_message)

    return chat_messages


def escape_markdown_v2(text: str) -> str:
    SPECIAL_CHARS = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    escaped_text = text
    for char in SPECIAL_CHARS:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text
