from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import random
import os
import json
from dotenv import load_dotenv
import nest_asyncio
from datetime import datetime
from LLM.llm_settings_manager import LLMSettings
from prompts.react import SYSTEM_PROMPT


from tools.utils import get_today_date_tool, greeting_tool, crypto_knowledge_tool
from tools.get_wallets import get_wallets_tool
from tools.get_positions import get_positions_tool
from tools.search_tokens import search_tokens_tool

from langchain.agents.agent import AgentOutputParser
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI

# Fix lỗi event loop
nest_asyncio.apply()
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Không tìm thấy TELEGRAM_BOT_TOKEN trong file .env")

llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model="gemini-pro",
    temperature=0,
    timeout=30,
    max_retries=2,
)

tools = [
    get_positions_tool,
    search_tokens_tool,
    get_wallets_tool,
    greeting_tool,
    crypto_knowledge_tool,
]


# template = '''You are RaidenX, a bot that helps buy or sell tokens. To buy or sell tokens, you need:

# 1. The token's address - if there are multiple tokens, ask the user which one to choose
# 2. Amount:
#    - For buying: Amount in SUI
#    - For selling: Percentage options (25%, 50%, 75%, 100%)

# Check the user's intention carefully. If they want to buy or sell tokens, collect all necessary information.

# If the user's question is not related to any available actions, provide answers based on your knowledge about cryptocurrency, blockchain technology, trading, and market dynamics.

# You have access to the following tools:

# {tools}

# Use the following format:

# Question: the input question to be answered
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original question

# Let's begin!

# Question: {input}
# Thought:{agent_scratchpad}'''

ReACT_PROMPT = """You are Bot Assistant, a bot that helps users buy or sell tokens, as well as provide information about tokens, user positions, and wallet details. To assist users effectively, follow these guidelines:

### For Buying or Selling Tokens:
1. **Token Address**: Required for trading. If multiple tokens match the query, ask the user to choose one.
2. **Amount**:
   - For buying: Amount in SUI.
   - For selling: Percentage options (25%, 50%, 75%, 100%).

### For Providing Information:
1. **Token Information**: Use tools to retrieve details like token name, symbol, price, and contract address.
2. **User Positions**: Use tools to fetch the user's token holdings and balances in their wallets.
3. **Wallet Information**: Use tools to retrieve wallet addresses and associated metadata.

Check the user's intention carefully. If they want to buy, sell, or retrieve information, collect all necessary details before proceeding.

If the user's question is not related to the above, provide answers based on your knowledge about cryptocurrency, blockchain technology, trading, and market dynamics.

You have access to the following tools:

{tools}

MUST use following format:

Question: the input question to be answered
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, in a JSON format representing the kwargs (e.g., {{"input": "hello world"}})
Observation: the result of the action
... (Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

### Additional Rules for Function Calling:
1. **Missing Parameters**: If a tool requires specific parameters and they are not provided, DO NOT call the tool. Instead, ask the user for the missing information - It the final answer.
   - Example: If the `search_token_tool` requires a `query` and the user only says "Find tokens," respond with: "Can you provide more details, like the token name, symbol, or keywords?"
2. **Confirm Intent**: Always confirm the user's intent before proceeding. For example, if the user says "I want to buy tokens," ask: "Which token are you interested in, and how much SUI would you like to spend?"
3. **Structured Input**: Ensure all inputs to tools are in valid JSON format. Do NOT call a tool with incomplete or invalid inputs.
4. **Tool Priority**: Use tools to retrieve information whenever possible. Avoid relying solely on your knowledge base unless no tools are applicable. With Greeting or ask what chatbot can do, you can answer directly.
5. **Repeat Until Complete**: If the user provides partial information, keep asking for the remaining details until all required parameters are available. When ask for more information, must show that what you already have, what need user to confirm.
    Example: User ask token relate to X -> must show all token relate to X as result, ask user to choose one token if interest.
Let's begin!
User informations:
userId: {userId}, userName: {userName}, displayName: {displayName}
Previous messages:
{chat_history}

USER'S INPUT
Current message:
{query}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate.from_template(ReACT_PROMPT)

react_agent = create_react_agent(llm, tools=tools, prompt=react_prompt)

react_agent_executor = AgentExecutor(
    agent=react_agent, tools=tools, verbose=True, handle_parsing_errors=True
)


HISTORY_FILE = "chat_history.json"


def load_chat_history():
    """Load lịch sử chat từ file JSON"""
    try:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Nếu file không tồn tại hoặc trống, tạo file mới với dict rỗng
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
    except json.JSONDecodeError:
        print(f"Lỗi khi đọc file {HISTORY_FILE}. Tạo file mới.")
        # Nếu file bị hỏng, tạo file mới với dict rỗng
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def save_chat_history(history):
    """Lưu lịch sử chat vào file JSON"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# Load lịch sử chat khi khởi động
chat_history = load_chat_history()

# Khởi tạo LLM client
llm_client = LLMSettings()


def escape_markdown_v2(text: str) -> str:
    """Escape các ký tự đặc biệt trong markdown v2"""
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # chat_id = str(update.effective_chat.id)
    # user = update.effective_user
    chat_id = "2104920255"
    user = "Harry Dang"
    user_message = update.message.text
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Khởi tạo lịch sử cho chat mới
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # Lưu tin nhắn của user
    chat_history[chat_id].append(
        {"role": "user", "content": user_message, "time": current_time, "type": "user"}
    )
    # Tạo prompt cho LLM với system prompt và lịch sử chat
    # Take the last 10 messages
    last_five_messages = chat_history[chat_id][-10:]

    # Convert to text-only format
    chat_history_text = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in last_five_messages
            if "role" in msg and "content" in msg  # Ensure the keys exist
        ]
    )

    # Lấy câu trả lời từ LLM
    bot_response = react_agent_executor.invoke(
        {
            "query": user_message,
            "chat_history": chat_history_text,
            "userId": chat_id,
            "userName": user,
            "displayName": "Harry Dang",
        }
    )

    bot_response = bot_response["output"]

    # Lưu câu trả lời của bot
    chat_history[chat_id].append(
        {"sender": "Bot", "message": bot_response, "time": current_time, "type": "bot"}
    )

    # Giữ 50 tin nhắn gần nhất
    if len(chat_history[chat_id]) > 50:
        chat_history[chat_id] = chat_history[chat_id][-50:]

    # Lưu vào file
    save_chat_history(chat_history)

    # Escape ký tự đặc biệt và gửi tin nhắn
    try:
        escaped_response = escape_markdown_v2(bot_response)
        await update.message.reply_text(
            escaped_response, parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        # Fallback: gửi tin nhắn không có định dạng nếu có lỗi
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
    # Thay đổi cách chạy event loop
    try:
        import asyncio

        if asyncio._get_running_loop() is not None:
            # Nếu event loop đang chạy, sử dụng nó
            asyncio.run_coroutine_threadsafe(main(), asyncio._get_running_loop())
        else:
            # Nếu chưa có event loop nào chạy, tạo mới
            asyncio.run(main())
    except Exception as e:
        print(f"Lỗi khởi động bot: {e}")
