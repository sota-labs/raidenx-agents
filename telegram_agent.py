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
    raise ValueError("Missing Telegram authentication information in .env file")

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='(?!/).+'))
async def handle_message(event):
    try:
        # Kiểm tra xem tin nhắn có phải từ chat riêng tư không
        if not event.is_private:
            return  # Bỏ qua tin nhắn nếu không phải chat riêng tư
            
        chat_id = str(event.chat_id)
        user = event.sender.first_name if event.sender else "Unknown User"
        
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

        try:
            bot_response = react_chat(
                query=user_message,
                llm=llm,
                chat_history=chat_history_message,
                userId=chat_id,
                userName=user,
                displayName=user,
            )
        except ValueError as e:
            if "Reached max iterations" in str(e):
                bot_response = "Sorry, I cannot process your request. Please try again with a clearer question."
            else:
                bot_response = f"An error occurred: {str(e)}"
        except Exception as e:
            bot_response = f"An unexpected error occurred: {str(e)}"

        chat_history[chat_id].append(
            {"role": "assistant", "content": bot_response, "time": current_time}
        )

        if len(chat_history[chat_id]) > 20:
            chat_history[chat_id] = chat_history[chat_id][-20:]

        save_chat_history(chat_history)

        try:
            # Bỏ việc escape và gửi tin nhắn thông thường
            await event.reply(bot_response)
        except Exception as e:
            print(f"Error sending message: {e}")
            await event.reply(bot_response)

    except Exception as e:
        print(f"Error in handle_message: {e}")
        await event.reply("Sorry, an error occurred while processing your message.")

def main():
    try:
        print("Bot has started...")
        client.run_until_disconnected()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Bot startup error: {e}")
