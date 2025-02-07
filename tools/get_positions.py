import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from auth.jwt_generator import get_jwt
from config import settings

def get_positions_by_token(token_address: str, jwt_token: str) -> list:
    """
    Get token positions from a user's wallet for a specific token address
    
    Args:
        token_address (str): Token contract address
        jwt_token (str): Authorization token
        
    Returns:
        list: List of positions containing:
            - symbol (str): Token symbol
            - name (str): Token name
            - address (str): Token contract address
            - balance (float): Token balance
            - wallet_address (str): Wallet address holding the token
    """
    try:
        url = f"{settings.raiden.api_insight_url}/sui/api/v1/my/positions/{token_address}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('docs'):
            return []
            
        return [
            {
                'symbol': pos['token']['symbol'],
                'name': pos['token']['name'],
                'address': pos['token']['address'],
                'balance': pos['balance'],
                'wallet_address': pos['walletName']
            }
            for pos in data['docs']
        ]
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unknown error: {str(e)}")