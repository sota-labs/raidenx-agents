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
from llama_index.core.tools import BaseTool, ToolOutput
from utils.output_parser import ReActOutputParser
from tools import (
    get_positions_by_token,
    get_wallet_balance,
    search_token,
    buy_token,
    sell_token,
    get_all_positions,
    scan_token,
    get_trending_pairs,
)

from prompts.react import REACT_CHAT_SYSTEM_HEADER_CUSTOM
from LLM.llm_settings_manager import LLMSettingsManager
from utils.tool_history import ToolHistoryLogger

llm_manager = LLMSettingsManager()

llm = llm_manager.get_llm("gemini", model="models/gemini-1.5-pro")

tool_logger = ToolHistoryLogger()

class CustomReActChatFormatter(ReActChatFormatter):
    """ReAct chat formatter."""

    @property 
    def reasoning_steps(self):
        """Get the current reasoning steps."""
        return self._current_reasoning

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
        self._kwargs = kwargs
        self._current_reasoning = []

    def format(
        self,
        tools: Sequence[BaseTool],
        chat_history: List[ChatMessage],
        current_reasoning: Optional[List[BaseReasoningStep]] = None,
        **kwargs,
    ) -> List[ChatMessage]:
        """Format chat history into list of ChatMessage."""
        self._current_reasoning = current_reasoning or []

        format_args = {
            "tool_desc": "\n".join(get_react_tool_descriptions(tools)),
            "tool_names": ", ".join([tool.metadata.get_name() for tool in tools]),
        }

        if self.context:
            format_args["context"] = self.context

        combined_args = {**format_args, **self._kwargs}
        fmt_sys_header = self.system_header.format(**combined_args)
        reasoning_history = []
        for reasoning_step in self.reasoning_steps:
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


react_system_prompt = PromptTemplate(REACT_CHAT_SYSTEM_HEADER_CUSTOM)

tools = [
    FunctionTool.from_defaults(
        fn=get_trending_pairs,
        name="get_trending_pairs", 
        description=(
            "Get trending trading pairs on the market."
            """Input args:
                jwt_token (str): User's authorization token
                resolution (str, optional): Time frame (default: "5m")
                limit (int, optional): Max pairs to return (default: 5)"""
            "Output: Price, market cap, liquidity, volume and performance metrics"
        ),
    ),
    FunctionTool.from_defaults(
        fn=get_wallet_balance,
        name="get_wallet_balance",
        description=(
            "Check user's wallet balances."
            """Input args: 
                jwt_token (str): Authorization token"""
            "Output: List of wallet addresses and their SUI balances"
        ),
    ),
    FunctionTool.from_defaults(
        fn=search_token,
        name="search_token",
        description=(
            "Search for token information to assist with buying decisions. "
            """Input args: 
                query (str): Token name or symbol
                jwt_token (str): Authorization token"""
            "Output: Token address, name, symbol, current price, liquidity metrics, and key indicators for pre-purchase evaluation"
        ),
    ),
    FunctionTool.from_defaults(
        fn=buy_token,
        name="buy_token",
        description=(
            "Buy tokens."
            """Input args: 
                jwt_token (str): Authorization token
                token_address (str): Token contract address
                amount (float): Amount to buy in SUI
                wallet_address (str): User's wallet address"""
            "Output: Purchase transaction status"
        ),
    ),
    FunctionTool.from_defaults(
        fn=sell_token,
        name="sell_token",
        description=(
            "Sell tokens."
            """Input args: 
                jwt_token (str): Authorization token
                token_address (str): Token contract address
                percent (float): Percentage of tokens to sell
                wallet_address (str): User's wallet address"""
            "Output: Sell transaction status"
        ),
    ),
    FunctionTool.from_defaults(
        fn=get_all_positions,
        name="get_all_positions",
        description=(
            "Get all token positions from user's wallets to review holdings or prepare for selling."
            """Input args:
                jwt_token (str): Authorization token"""
            "Output: List of tokens with current balances, values, profit/loss metrics and other details needed for portfolio review or selling decisions"
        ),
    ),
    FunctionTool.from_defaults(
        fn=scan_token,
        name="scan_token",
        description=(
            "Analyze token's trading metrics."
            """Input args:
                token_address (str): Token contract address"""
            "Output: Price, market cap, liquidity, volume and transaction counts"
        ),
    ),
]


def react_chat(
    query: str,
    llm=None,
    chat_history: List[ChatMessage] = None,
    max_iterations=10,
    jwt_token=None,
):
    formatter = CustomReActChatFormatter(jwt_token=jwt_token)
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

# async def react_chat_stream(
#     query: str,
#     llm=None,
#     chat_history: List[ChatMessage] = None,
#     max_iterations=10,
#     userId="2104920255",
#     userName="RaidenX Agent",
#     displayName="RaidenX Agent",
# ):
#     formatter = CustomReActChatFormatter(
#         userId=userId, userName=userName, displayName=displayName
#     )
#     agent = ReActAgent.from_tools(
#         tools=tools,
#         llm=llm,
#         verbose=True,
#         chat_history=chat_history,
#         react_chat_formatter=formatter,
#         max_iterations=max_iterations,
#         output_parser=ReActOutputParser()
#     )
#     agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
    
#     response = agent.stream_chat(query)
#     print(response)
#     for token in response.response_gen:
#         yield str(token)

#     agent.reset()
