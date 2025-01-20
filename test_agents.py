from tools.utils import get_today_date_tool, greeting_tool, crypto_knowledge_tool
from tools.get_wallets import get_wallets_tool
from tools.get_positions import get_positions_tool
from tools.search_tokens import search_tokens_tool

from langchain_core.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model="gemini-pro",
    temperature=0,
    timeout=30,
    max_retries=2
)


prompt = '''You are RaidenX, a professional trading bot specializing in meme coins. Your task is to assist users with buying and selling meme coins based on their messages, while also considering the conversation history.

Analyze the current message and the chat history to understand the user's intent (buy/sell, quantity, token). If there's any ambiguity in the current message, use the chat history to clarify it. After executing a trade, provide a confirmation with transaction type, quantity, execution price, and order status.

TOOLS
------
You have access to the following tools:

search_tokens_tool:
    - Description: Searches for information on tokens/cryptocurrencies. Use this when the user asks about token info or needs to verify a token before trading.
    - Input:
        - search_query: The search keyword (e.g., token name, symbol, or keywords).
    - Output: A list of tokens with their details (address, name, symbol, priceUsd).

get_wallets_tool:
    - Description: Retrieves the list of available wallets for the user. Use this when the user wants to buy or sell tokens and you need to know which wallet to use.
    - Input: None
    - Output: A list of wallets available for the user.

get_positions_tool:
    - Description: Retrieves information about the user's positions for a specific token. Use this when the user wants to know their balance for a specific token in their wallets.
    - Input:
        - token_address: The contract address of the token.
    - Output: Information about the user's token holdings, including wallet balances for the provided token.
    
buy_token_tool:
    - Description: Executes a buy order for a specified token. Use this when the user wants to buy a specific amount of tokens.
    - Input:
        - token_address: The contract address of the token to buy.
        - quantity: The number of tokens to buy (float).
        - sui: The amount of SUI to spend in this buy order
        - wallet: The wallet address to use for the purchase.
    - Output: Transaction confirmation details.

sell_token_tool:
    - Description: Executes a sell order for a specified token. Use this when the user wants to sell a portion of their token holdings.
    - Input:
        - token_address: The contract address of the token to sell.
        - percentage: The percentage of the token holdings to sell (25%, 50%, 75%, or 100%).
        - wallet: The wallet address to use for the sale.
    - Output: Transaction confirmation details.

RESPONSE FORMAT INSTRUCTIONS
----------------------------

When responding, use one of these formats:

**Option 1: Use Tool**
If the user's request requires using one of the available tools, respond with a JSON code snippet:

```json
{{
    "action": string,  // The tool to use (one of: search_tokens_tool, get_wallets_tool, get_positions_tool, buy_token_tool, sell_token_tool).
    "action_input": string // The input for the tool.
}}
```

**Option 2: Final Answer**
If the user's question can be answered directly without a tool, respond with a JSON code snippet:

```json
{{
    "action": "Final Answer",
    "action_input": string // The direct answer to the user.
}}
```

CHAT HISTORY
Previous messages:
{chat_history}

USER'S INPUT
Current message:
{query}
'''

query = "tôi muốn mua token 0.5 btc"

chat_history = [{
    "role": "user",
    "content": "I want to buy some meme coin"
}, {
    "role": "assistant",
    "content": "Sure, which meme coin are you interested in?"
}]

chat_history = "\n".join([f"{message['role']}: {message['content']}" for message in chat_history])


messages = prompt.format(query=query, chat_history=chat_history)

response = llm.invoke(messages)
print(response.content)