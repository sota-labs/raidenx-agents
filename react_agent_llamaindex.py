from typing import List

from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini

from tools import get_positions_by_token, get_wallets, search_token

react_system_header_str = """\

You are Bot Assistant, a bot that helps users buy or sell tokens, as well as provide information about tokens, user positions, and wallet details. To assist users effectively, follow these guidelines:

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
    If user just greeting, you can greeting back without using any tool. 
    If you have enough input values for tool, you can use tool.
    Never imagine input for a tool. if you dont have enough information need, ask user till enough input values.
## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask. Tool can provide information for the answer, may be it not, but you should use tool retrieval for knowledge update. \
its build for custom company with detail information. \
If user just greeting, you can greeting withou any tool. But if user ask for information, you must use tool for more context. 
        E.g: What is your Line ID? - you use retrieval tool to search line ID of Lenso Wheel because you are LensoWheel chatbot assistant. \
            Retrieval tool will response with context. use it to answer question.
        You should use at least tool retrieval for more context. Priority use tool over your knowledge base.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.
```

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Here is User informations:
        userId="2104920255",
        userName="Harry Dang",
        displayName="Harry Dang",
## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""
react_system_prompt = PromptTemplate(react_system_header_str)

# userId: {userId}, userName: {userName}, displayName: {displayName}


def react_chat(
    query: str,
    llm=None,
    chat_history: List[ChatMessage] = None,
):
    print("Start Agent chain")
    tools = [
        FunctionTool.from_defaults(
            fn=get_positions_by_token,
            name="Get_Token_Position",
            description=(
                "Return positions of a specific token in user's wallets."
                """Input args: userId (str): The user's unique identifier.
                userName (str): The user's username.
                displayName (str): The user's display name.
                token_address (str): The token's contract address."""
                "Use this tool in crypto applications to check token balances, track holdings, or analyze wallet activity."
            ),
        ),
        FunctionTool.from_defaults(
            fn=get_wallets,
            name="Get_Wallet",
            description=(
                "Useful for retrieving wallet information associated with a user."
                """Input args: userId (str): The user's unique identifier.
                userName (str): The user's username.
                displayName (str): The user's display name."""
                "Use this tool in crypto applications to fetch wallet details for analysis, tracking, or integration."
            ),
        ),
        FunctionTool.from_defaults(
            fn=search_token,
            name="Search_Token",
            description=(
                "Useful for searching token/cryptocurrency information when buying or selling."
                """Input args: query (str): Token name, symbol, or related keywords (e.g., 'Blue', 'Cook', 'Island boy')."""
                "Use this tool in crypto applications to:"
                "- Find detailed token information (name, symbol, contract address, price)."
                "- Verify if a token exists and is tradeable on supported platforms."
                "- Identify the correct token for trading based on user queries."
                "- Retrieve a list of tokens matching the search query with basic details (address, name, symbol, priceUsd)."
            ),
        ),
    ]
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,
        chat_history=chat_history,
        # userId="2104920255",
        # userName="Harry Dang",
        # displayName="Harry Dang",
    )
    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    response = agent.chat(query)
    response = str(response)
    agent.reset()
    return response


chat_history = [
    ChatMessage(
        role=MessageRole.ASSISTANT,
        content="Hi there! Ready to help you with your crypto trading needs!",
    ),
    ChatMessage(role=MessageRole.USER, content="positions là gì"),
    ChatMessage(
        role=MessageRole.ASSISTANT,
        content="Positions are a way to describe the different ways that you can hold or trade cryptocurrencies. \
            There are two main types of positions: long positions and short positions. A long position means that\
                you are buying a cryptocurrency with the expectation that its price will go up. A short position \
                    means that you are selling a cryptocurrency with the expectation that its price will go down.",
    ),
    ChatMessage(role=MessageRole.USER, content="what is my wallet status"),
    ChatMessage(
        role=MessageRole.ASSISTANT,
        content="You have 5 wallets associated with your account.",
    ),
    # ChatMessage(
    #     role=MessageRole.USER, content="I want to buy some token relate with  Biden"
    # ),
    # ChatMessage(
    #     role=MessageRole.ASSISTANT,
    #     content="""I found several tokens related to "Biden". Please choose one from the following list by providing its symbol:

    #                 * SADJOE: Sad Joe Biden
    #                 * JOY: Joy Biden
    #                 * RIPBIDEN: RIPBIDEN
    #                 * BYEBIDEN: Official Bye Joe Biden
    #                 * BELBOTS: btcethltcbushobamatrumpbiden
    #                 * BTCSUI: btcethltcbushobamatrumpbidensui
    #                 * GETOUTBIDEN (two tokens with this symbol)
    #                 * FUCKBIDEN


    #                 Once you've selected a token, I'll need the amount you wish to buy (in SUI).""",
    # ),
    # ChatMessage(role=MessageRole.USER, content="What is price of token Fck biden"),
    # ChatMessage(
    #     role=MessageRole.ASSISTANT,
    #     content=""" * The user requested the price of the token with symbol "Fck Biden".  Due to the inappropriate nature of the symbol, I used the tool with the corrected symbol "FUCKBIDEN".
    #                 * The Search_Token tool returned the following information for the token with symbol "FUCKBIDEN":
    #                 * **Address:** 0x6cc9f2a115f224c59bfdec71516ba037a4c3ef518137fd86a60035ca1f0e28a3::simple_token::SIMPLE_TOKEN
    #                 * **Name:** SIMPLE_TOKEN
    #                 * **Symbol:** FUCKBIDEN
    #                 * **Price (USD):** 8.042233734671179E-7  (This is a very small price, approximately 0.0000008 USD)""",
    # ),
    # ChatMessage(role=MessageRole.USER, content="How can i buy it?"),
    # ChatMessage(
    #     role=MessageRole.ASSISTANT,
    #     content=" To buy the FUCKBIDEN token, please tell me how much SUI you'd like to spend.  Once I have that information, \
    #         I can guide you through the purchase process.",
    # ),
]


llm = Gemini(
    model="models/gemini-1.5-flash",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)
query = "I want to buy the cheapest token relate with  `Trump`. Can you check my Wallets and caculate how much i can buy?"
response = react_chat(query=query, chat_history=chat_history, llm=llm)
print("-------------")
print(f"Final Response: \n {response}")
