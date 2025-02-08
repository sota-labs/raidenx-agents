import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from config import settings
from tools.get_positions import get_all_positions

def search_token(query: str, jwt_token: str) -> dict:
    """
    Search for tokens based on keywords

    Args:
        query (str): Search keyword (e.g., 'BTC', 'ETH')
        
    Returns:
        dict: Dictionary containing list of tokens with:
            - tokens (list): List of token information:
                - address (str): Token contract address
                - name (str): Token name
                - symbol (str): Token symbol
                - priceUsd (float): Current token price in USD
                
    Raises:
        RequestException: If API request fails
        Exception: If search operation fails with status code and error message
    """
    
    try:
        positions = get_all_positions(jwt_token)
    except Exception as e:
        positions = []
        print(f"Error getting positions: {str(e)}")
    
    url = f"{settings.raiden.api_common_url}/api/v1/search"
    headers = {
        "accept": "application/json"
    }

    params = {
        "search": query,
        "page": 1,
        "limit": 5
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = []
        for doc in data.get('docs', []):
            liquidityUsd = float(doc.get('liquidityUsd', 0))
            token_info = doc.get('tokenBase', {})
            position_token_addresses = [pos['token_address'] for pos in positions]
            if liquidityUsd > 10000 or token_info.get('address') in position_token_addresses:
                results.append({
                    'address': token_info.get('address'),
                    'name': token_info.get('name'),
                    'symbol': token_info.get('symbol'),
                    'priceUsd': token_info.get('priceUsd'),
                    'liquidityUsd': liquidityUsd
                })
                
        if not results:
            return f'No tokens found for {query}'
        
        results.sort(key=lambda x: float(x['liquidityUsd'] or 0), reverse=True)
        return {'tokens': results[0:5]}
    else:
        raise Exception(f"Error searching tokens: {response.status_code} - {response.text}")

# print(search_token('huu'))