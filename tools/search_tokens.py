import requests
from langchain.agents import Tool
from pydantic import BaseModel, Field
import json
from tools.utils import json_to_dict
class SearchTokensInput(BaseModel):
    search_query: str = Field(..., description="Search keyword (e.g., 'BTC')")
    
    class Config:
        extra = "forbid"
# @json_to_dict
def search_token(query: str) -> dict:
    """
    Search for tokens based on keywords
    
    Args:
        input: Can be either SearchTokensInput object or string
            - If SearchTokensInput: Object containing search information
            - If string: Direct search query
        
    Returns:
        dict: List of tokens with basic information (address, name, symbol, priceUsd)
    """
    url = "https://api.dextrade.bot/api/v1/search"
    headers = {
        "accept": "application/json"
    }

    params = {
        "search": query,
        "page": 1,
        "limit": 3
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = []
        for doc in data.get('docs', []):
            token_info = doc.get('tokenBase', {})
            results.append({
                'address': token_info.get('address'),
                'name': token_info.get('name'),
                'symbol': token_info.get('symbol'),
                'priceUsd': token_info.get('priceUsd')
            })
        return {'tokens': results[0:5]}
    else:
        raise Exception(f"Error searching tokens: {response.status_code} - {response.text}")
    
search_tokens_tool = Tool(
    name="Search Token",
    func=search_token,
    description=(
        "Useful for searching token/cryptocurrency information when buying or selling."
        """Input args: query (str): Token name, symbol, or related keywords (e.g., 'Blue', 'Cook', 'Island boy')."""
        "Use this tool in crypto applications to:"
        "- Find detailed token information (name, symbol, contract address, price)."
        "- Verify if a token exists and is tradeable on supported platforms."
        "- Identify the correct token for trading based on user queries."
        "- Retrieve a list of tokens matching the search query with basic details (address, name, symbol, priceUsd)."
    )
)
