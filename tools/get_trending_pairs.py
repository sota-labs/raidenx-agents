import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from config import settings

def get_trending_pairs(jwt_token: str = "", resolution: str = "5m", limit: int = 5) -> dict:
    """
    Get a list of trending trading pairs
    
    Args:
        resolution (str): Time frame (default: "5m")
        limit (int): Maximum number of pairs to return (default: 5)
        
    Returns:
        dict: Dictionary containing list of trading pairs with information:
            - pairs (list): List of trading pairs:
                - pairId (str): ID of the trading pair
                - dex (str): Name of the exchange
                - tokenBase (dict): Base token information
                    - address (str): Token contract address
                    - name (str): Token name
                    - symbol (str): Token symbol
                    - priceUsd (float): Token price in USD
                - liquidityUsd (float): Liquidity in USD
                - volumeUsd (float): Trading volume in USD
                - priceChange (dict): Price change percentages for different timeframes
                    - 5m (float): 5-minute change
                    - 1h (float): 1-hour change
                    - 6h (float): 6-hour change
                    - 24h (float): 24-hour change
    """
    try:
        if limit <= 0 or limit > 10:
            limit = 10
            
        valid_resolutions = ["5m", "1h", "6h", "24h"]
        if resolution not in valid_resolutions:
            resolution = "24h"
            
        url = f"{settings.raiden.api_common_url}/api/v1/sui/pairs/trending"
        
        params = {
            "page": 1,
            "limit": limit,
            "resolution": resolution,
            "network": "sui"
        }
        
        headers = {
            "accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            sorted_data = sorted(data, key=lambda x: float(x.get('liquidityUsd', 0)), reverse=True)
            
            pairs = []
            
            for pair in sorted_data[:limit]:
                price_usd = float(pair.get('tokenBase', {}).get('priceUsd', 0))
                liquidity_usd = float(pair.get('liquidityUsd', 0))
                volume_usd = float(pair.get('volumeUsd', 0))
                
                token_info = (
                    f"## {pair.get('tokenBase', {}).get('symbol')} | ${'{:,.4f}'.format(price_usd)}\n"
                    f"`{pair.get('tokenBase', {}).get('address')}`\n\n"
                    f"📈 Changes: 5m: {'{:.2f}'.format(pair.get('stats', {}).get('percent', {}).get('5m', 0))}% | "
                    f"1h: {'{:.2f}'.format(pair.get('stats', {}).get('percent', {}).get('1h', 0))}% | "
                    f"24h: {'{:.2f}'.format(pair.get('stats', {}).get('percent', {}).get('24h', 0))}%\n"
                    f"💰 Liquidity: ${'{:,.2f}'.format(liquidity_usd)} | Volume: ${'{:,.2f}'.format(volume_usd)}\n"
                )
                
                pairs.append({
                    'markdown': token_info,
                    'tokenBase': {
                        'address': pair.get('tokenBase', {}).get('address'),
                        'name': pair.get('tokenBase', {}).get('name'),
                        'symbol': pair.get('tokenBase', {}).get('symbol'),
                        'priceUsd': price_usd
                    },
                    'liquidityUsd': liquidity_usd,
                    'volumeUsd': volume_usd,
                    'priceChange': {
                        '5m': pair.get('stats', {}).get('percent', {}).get('5m', 0),
                        '1h': pair.get('stats', {}).get('percent', {}).get('1h', 0),
                        '6h': pair.get('stats', {}).get('percent', {}).get('6h', 0),
                        '24h': pair.get('stats', {}).get('percent', {}).get('24h', 0)
                    }
                })
            
            return {'pairs': pairs}
        else:
            raise Exception(f"Error fetching trending pairs: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unknown error: {str(e)}")
    
    
# print(get_trending_pairs())