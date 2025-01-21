from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import nest_asyncio
from utils.chat_session import (
    load_chat_history,
    save_chat_history,
    convert_dict_to_chat_messages,
    escape_markdown_v2,
)
from agents import react_chat, llm
from datetime import datetime

nest_asyncio.apply()
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Thiếu thông tin xác thực Telegram trong file .env")

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='(?!/).+'))
async def handle_message(event):
    chat_id = "2104920255" 
    user = "Harry Dang"    
    user_message = event.message.text
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history = load_chat_history()

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append(
        {"role": "user", "content": user_message, "time": current_time}
    )
    last_five_messages = chat_history[chat_id][-10:]

    chat_history_message = convert_dict_to_chat_messages(last_five_messages)

    bot_response = react_chat(
        query=user_message,
        llm=llm,
        chat_history=chat_history_message,
        userId=chat_id,
        userName=user,
        displayName=user,
    )

    chat_history[chat_id].append(
        {"role": "assistant", "content": bot_response, "time": current_time}
    )

    if len(chat_history[chat_id]) > 50:
        chat_history[chat_id] = chat_history[chat_id][-50:]

    save_chat_history(chat_history)

    try:
        escaped_response = escape_markdown_v2(bot_response)
        await event.reply(escaped_response, parse_mode='markdown')
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn có định dạng: {e}")
        await event.reply(bot_response)

def main():
    try:
        print("Bot đã khởi động...")
        client.run_until_disconnected()
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi khởi động bot: {e}")
