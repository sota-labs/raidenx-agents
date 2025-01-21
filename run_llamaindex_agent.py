from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv
import nest_asyncio
from utils.chat_session import (
    load_chat_history,
    save_chat_history,
    convert_dict_to_chat_messages,
    escape_markdown_v2,
)
from react_agent_llamaindex import react_chat, llm
from datetime import datetime

nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Không tìm thấy TELEGRAM_BOT_TOKEN trong file .env")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # chat_id = str(update.effective_chat.id)
    # user = update.effective_user
    chat_id = "2104920255"
    user = "Harry Dang"
    user_message = update.message.text
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


    # Save new chat to file
    chat_history[chat_id].append(
        {"role": "assistant", "content": bot_response, "time": current_time}
    )

    if len(chat_history[chat_id]) > 50:
        chat_history[chat_id] = chat_history[chat_id][-50:]

    save_chat_history(chat_history)

    try:
        escaped_response = escape_markdown_v2(bot_response)
        await update.message.reply_text(
            escaped_response, parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn có định dạng: {e}")
        await update.message.reply_text(bot_response)


async def main():
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("Bot đã khởi động...")
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    try:
        import asyncio

        if asyncio._get_running_loop() is not None:
            asyncio.run_coroutine_threadsafe(main(), asyncio._get_running_loop())
        else:
            asyncio.run(main())
    except Exception as e:
        print(f"Lỗi khởi động bot: {e}")
