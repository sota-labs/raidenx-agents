from typing import List, Optional, Sequence

from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from llama_index.core.agent.react.formatter import (
    ReActChatFormatter,
    get_react_tool_descriptions,
)
from llama_index.core.agent.react.prompts import (
    CONTEXT_REACT_CHAT_SYSTEM_HEADER,
    REACT_CHAT_SYSTEM_HEADER,
)
from llama_index.core.agent.react.types import (
    BaseReasoningStep,
    ObservationReasoningStep,
)
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.llms.gemini import Gemini
from llama_index.core.tools import BaseTool, ToolOutput
from utils.output_parser import ReActOutputParser
from tools import (
    get_positions_by_token,
    get_wallets,
    search_token,
    buy_token,
    sell_token,
)

llm = Gemini(
    model="models/gemini-1.5-flash",
)


class CustomReActChatFormatter(ReActChatFormatter):
    """ReAct chat formatter."""

    def __init__(
        self,
        system_header: str = REACT_CHAT_SYSTEM_HEADER,  # default system header
        context: str = "",  # default context (optional)
        **kwargs,
    ):
        """
        Initialize the CustomReActChatFormatter.

        Args:
            system_header (str): The system header template string.
            context (str): Additional context to include in the format.
            **kwargs: Additional keyword arguments to store and use in formatting.
        """
        super().__init__(system_header=system_header, context=context)
        self._kwargs = kwargs  # Store additional kwargs for later use

    def format(
        self,
        tools: Sequence[BaseTool],
        chat_history: List[ChatMessage],
        current_reasoning: Optional[List[BaseReasoningStep]] = None,
        **kwargs,
    ) -> List[ChatMessage]:
        """Format chat history into list of ChatMessage."""
        current_reasoning = current_reasoning or []

        # Initialize format_args with tool descriptions and names
        format_args = {
            "tool_desc": "\n".join(get_react_tool_descriptions(tools)),
            "tool_names": ", ".join([tool.metadata.get_name() for tool in tools]),
        }
        # Add context to format_args if it exists
        if self.context:
            format_args["context"] = self.context

        # Combine format_args with kwargs
        combined_args = {**format_args, **self._kwargs}
        # Format the system header using the combined arguments
        fmt_sys_header = self.system_header.format(**combined_args)
        # Format reasoning history as alternating user and assistant messages
        reasoning_history = []
        for reasoning_step in current_reasoning:
            if isinstance(reasoning_step, ObservationReasoningStep):
                message = ChatMessage(
                    role=MessageRole.USER,
                    content=reasoning_step.get_content(),
                )
            else:
                message = ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=reasoning_step.get_content(),
                )
            reasoning_history.append(message)

        return [
            ChatMessage(role=MessageRole.SYSTEM, content=fmt_sys_header),
            *chat_history,
            *reasoning_history,
        ]

    @classmethod
    def from_defaults(
        cls,
        system_header: Optional[str] = None,
        context: Optional[str] = None,
    ) -> "CustomReActChatFormatter":
        """Create ReActChatFormatter from defaults."""
        if not system_header:
            system_header = (
                REACT_CHAT_SYSTEM_HEADER
                if not context
                else CONTEXT_REACT_CHAT_SYSTEM_HEADER
            )

        return CustomReActChatFormatter(
            system_header=system_header,
            context=context or "",
        )
        
def custom_failure_handler(callback_manager, exception):
    error_message = f"The agent encountered an error: {str(exception)}"
    return ToolOutput(content=error_message, tool_name="Error Handler")

REACT_CHAT_SYSTEM_HEADER_CUSTOM = """\

You are RaidenX Bot Assistant, a bot that helps users buy or sell tokens, as well as provide information about tokens, user positions, and wallet details. To assist users effectively, follow these guidelines:

### For Buying or Selling Tokens:
1. **Token Address**: Required for trading. If multiple tokens match the query, ask the user to choose one.
2. **Amount**:
   - For buying: Amount in SUI.
   - For selling: Percentage options (25%, 50%, 75%, 100%).

### For Providing Information:
1. **Token Information**: Use tools to retrieve details like token name, symbol, price, and contract address. Should response to user Name, Price and Contract address.
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
to complete each subtask.
If user just greeting, you can greeting without any tool. But if user ask for information, you must use tool for more context. 


You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, **MUST** use the following format - Start with `Thought` in all case:

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

MUST ALWAYS start with a Thought.

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
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Here is User informations:
userId: {userId}, userName: {userName}, displayName: {displayName}

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""
react_system_prompt = PromptTemplate(REACT_CHAT_SYSTEM_HEADER_CUSTOM)

tools = [
    FunctionTool.from_defaults(
        fn=get_positions_by_token,
        name="get_token_position",
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
        name="get_wallet",
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
        name="search_token",
        description=(
            "Useful for searching token/cryptocurrency information when buying or selling. Should response last user with Address token"
            """Input args: query (str): Token name, symbol, or related keywords (e.g., 'Blue', 'Cook', 'Island boy')."""
            "Use this tool in crypto applications to:"
            "- Find detailed token information (name, symbol, contract address, price)."
            "- Verify if a token exists and is tradeable on supported platforms."
            "- Identify the correct token for trading based on user queries."
            "- Retrieve a list of tokens matching the search query with basic details (address, name, symbol, priceUsd)."
        ),
    ),
    FunctionTool.from_defaults(
        fn=buy_token,
        name="buy_token",
        description=(
            "Status of purchase"
            """Input args: userId (str): The user's unique identifier.
                userName (str): The user's username.
                displayName (str): The user's display name.
                token_address (str): The token's contract address.
                amount (float): The Amount of token in SUI network want to buy."""
            "Use this tool in crypto applications when user want to buy an token by token"
        ),
    ),
    FunctionTool.from_defaults(
        fn=sell_token,
        name="sell_token",
        description=(
            "Status of purchase."
            """Input args: userId (str): The user's unique identifier.
                userName (str): The user's username.
                displayName (str): The user's display name.
                token_address (str): The token's contract address."""
            "Use this tool in crypto applications when user want to sell a token"
        ),
    ),
]


def react_chat(
    query: str,
    llm=None,
    chat_history: List[ChatMessage] = None,
    max_iterations=10,
    userId="2104920255",
    userName="Harry Dang",
    displayName="Harry Dang",
):
    formatter = CustomReActChatFormatter(
        userId=userId, userName=userName, displayName=displayName
    )
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,
        chat_history=chat_history,
        react_chat_formatter=formatter,
        max_iterations=max_iterations,
        output_parser=ReActOutputParser()
    )
    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    response = agent.chat(query)
    response = str(response)

    agent.reset()
    return response
