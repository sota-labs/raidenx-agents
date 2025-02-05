import requests
from config import config

def get_top_pair(token_address: str) -> dict:
    """
    Get the top pair for a given token

    Args:
        token_address (str): Token address
        
    Returns:
        dict: Top pair for the given token

    The API returns detailed information about the top trading pair for a token with the following structure:
    {
        "network": str,           # Network name (e.g. "sui")
        "dex": {                  # DEX information
            "network": str,       # DEX network
            "dex": str,          # DEX identifier
            "name": str,         # DEX name
            "version": str       # DEX version
        },
        "pairId": str,           # Unique pair identifier
        "poolId": str,           # Pool identifier
        "tokenBase": {           # Base token information
            "address": str,      # Token contract address
            "name": str,         # Token name
            "symbol": str,       # Token symbol
            "decimals": int,     # Token decimals
            "price": str,        # Current price
            "priceUsd": str,     # Price in USD
            "volumeUsd": str     # Volume in USD
        },
        "tokenQuote": {          # Quote token information (similar structure to tokenBase)
            "address": str,
            "name": str,
            "symbol": str,
            "decimals": int,
            "price": str,
            "priceUsd": str,
            "volumeUsd": str
        },
        "liquidity": str,        # Pool liquidity
        "liquidityUsd": str,     # Pool liquidity in USD
        "volume": str,           # Trading volume
        "volumeUsd": str,        # Trading volume in USD
    }
    """
    
    try:
        url = f"{config.RAIDENX_CONFIG['api_common_url']}/api/v1/sui/tokens/{token_address}/top-pair"
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting top pair: {str(e)}")