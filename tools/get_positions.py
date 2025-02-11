import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from auth.jwt_generator import get_jwt
from tools.get_wallets import get_wallet_balance
from config import settings

def get_positions_by_token(token_address: str, jwt_token: str) -> str:
    """
    Get token positions from a user's wallet for a specific token address
    
    Args:
        token_address (str): Token contract address
        jwt_token (str): Authorization token
        
    Returns:
        str: Markdown formatted output containing token positions
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
        
        def format_number(num: float) -> str:
            if num < 1000:
                return f"${num:.2f}"
            elif num < 1000000:
                return f"${num/1000:.1f}K"
            else:
                return f"${num:,.0f}"
        
        if not data.get('docs'):
            return "### No positions found"
            
        markdown_output = "### Your Positions\n\n"
        
        for pos in data['docs']:
            balance = float(pos['balance'])
            markdown_output += (
                f"### {pos['token']['symbol']}\n"
                f"💰 Balance: `{balance:.4f}`\n"
            )
            
        return markdown_output
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unknown error: {str(e)}")

def get_all_positions(jwt_token: str) -> str:
    """
    Get all positions from user's wallets
    
    Args:
        jwt_token (str): Authorization token
        
    Returns:
        str: Markdown formatted output containing all positions
    """
    try:
        wallet_info = get_wallet_balance(jwt_token)
        
        if not wallet_info or not wallet_info.get('address'):
            raise Exception("No wallet found. Please create a wallet first.")
            
        wallet_address = wallet_info['address']
        
        base_url = f"{settings.raiden.api_insight_url}/sui/api/v1/my/positions"
        params = {
            "closed": False,
            "isHidden": False,
            "walletAddress": wallet_address
        }
            
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('docs'):
            return "**🔍 No positions yet. Start trading now to build your portfolio!**"
            
        markdown_output = "**All Positions**\n\n"
        
        for pos in data['docs']:
            balance = float(pos['balance'])
            token_address = pos['token'].get('address', 'N/A')
            markdown_output += f"**{pos['token']['symbol']}** `{balance:.4f}` | `{token_address}` |  "
            
        return markdown_output
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))
    
    
def get_all_positions_data(jwt_token: str) -> list:
    """
    Get all positions from user's wallets
    
    Args:
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
        wallet_info = get_wallet_balance(jwt_token)
        
        # Check if wallet exists
        if not wallet_info or not wallet_info.get('address'):
            raise Exception("No wallet found. Please create a wallet first.")
            
        wallet_address = wallet_info['address']
        
        base_url = f"{settings.raiden.api_insight_url}/sui/api/v1/my/positions"
        params = {
            "closed": False,
            "isHidden": False,
            "walletAddress": wallet_address
        }
            
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('docs'):
            return []
            
        return [
            {
                'symbol': pos['token']['symbol'],
                'name': pos['token']['name'],
                'token_address': pos['token']['address'],
                'balance': pos['balance'],
                'wallet_address': pos['walletName']
            }
            for pos in data['docs']
        ]
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))
    
    
# print(get_all_positions(jwt_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIyMTA0OTIwMjU1IiwidXNlck5hbWUiOiJIYXJyeSIsImRpc3BsYXlOYW1lIjoiSGFycnkiLCJpYXAiOm51bGwsImlhdCI6MTczODkyMTk4OCwiZXhwIjoxNzQxNTEzOTg4fQ.xymjU6tzhqd0r3nO74JY-__TSINbHduPvzDFi2NX7zU'))