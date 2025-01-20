import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.utils import get_today_date_tool
from tools.get_wallets import get_wallets_tool
from tools.get_positions import get_positions_tool
from tools.search_tokens import search_tokens_tool


from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents import create_tool_calling_agent

from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

from prompts.react import prompt_react

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model="gemini-pro",
    temperature=0,
    timeout=30,
    max_retries=2
)

tools = [get_today_date_tool, get_wallets_tool, get_positions_tool, search_tokens_tool]

for tool in tools:
    print(f"Tool name: {tool.name}")
    print(f"Tool description: {tool.description}")
    print(f"Tool args: {tool.args}")
    print(f"Tool args schema: {tool.args_schema}")

# prompt_react = hub.pull("hwchase17/react")

# react_agent = create_react_agent(llm, tools=tools, prompt=prompt_react)

# react_agent_executor = AgentExecutor(
#     agent=react_agent, 
#     tools=tools, 
#     verbose=True, 
#     handle_parsing_errors=True
# )











