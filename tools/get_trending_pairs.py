import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from config import settings

def get_trending_pairs(resolution: str = "5m", limit: int = 5) -> str:
    """
    Get a list of trending trading pairs and return as formatted markdown
    
    Args:
        resolution (str): Time frame (default: "5m")
        limit (int): Maximum number of pairs to return (default: 5)
        
    Returns:
        str: Formatted markdown string containing trending pairs information
    """
    try:
        if limit <= 0 or limit > 5:
            limit = 5
            
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
            
            markdown_output = f"**Trending Pairs ({resolution})**\n\n"
            
            def format_number(num: float) -> str:
                if num < 1000:
                    return f"${num:.2f}"
                elif num < 1000000:
                    return f"${num/1000:.1f}K"
                else:
                    return f"${num:,.0f}"
            
            for pair in sorted_data[:limit]:
                price_usd = float(pair.get('tokenBase', {}).get('priceUsd', 0))
                liquidity_usd = float(pair.get('liquidityUsd', 0))
                volume_usd = float(pair.get('volumeUsd', 0))
                
                markdown_output += (
                    f"**{pair.get('tokenBase', {}).get('symbol')}** | 💰 ${price_usd:.4f} | 📈 5m: `{'{:+.2f}%'.format(pair.get('stats', {}).get('percent', {}).get('5m', 0))}` | 1h: `{'{:+.2f}%'.format(pair.get('stats', {}).get('percent', {}).get('1h', 0))}` | 24h: `{'{:+.2f}%'.format(pair.get('stats', {}).get('percent', {}).get('24h', 0))}`\n"
                    f"💧 Liquidity: `{format_number(liquidity_usd)}` | 📊 Volume: `{format_number(volume_usd)}`\n\n"
                )
            
            return markdown_output
        else:
            raise Exception(f"Error fetching trending pairs: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unknown error: {str(e)}")
    
    
# print(get_trending_pairs())