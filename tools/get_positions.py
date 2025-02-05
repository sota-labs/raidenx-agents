import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
from config import config
from tools.utils import json_to_dict


# @json_to_dict
def get_positions_by_token(userId: str, userName: str, displayName: str, token_address: str) -> dict:
    """
    Get positions information for a specific token in wallets
    
    Args:
        userId (str): User ID
        userName (str): Username
        displayName (str): Display name
        token_address (str): Token address to check
        
    Returns:
        dict: Token positions information
    """
    try:
        jwt_token = get_jwt(userId, userName, displayName)
        
        url = f"{config.RAIDENX_CONFIG['api_insight_url']}/sui/api/v1/my/positions/{token_address}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                if not response_data.get('docs'):
                    return f"No positions found for token {token_address}"
                
                positions = []
                for position in response_data['docs']:
                    token_data = {}
                    token_data['symbol'] = position['token']['symbol']
                    token_data['name'] = position['token']['name']
                    token_data['address'] = position['token']['address']
                    token_data['balance'] = position['balance']
                    token_data['wallet_address'] = position['walletName']
                    positions.append(token_data)
                return positions
            except (KeyError, IndexError) as e:
                raise Exception(f"Error processing response data: {str(e)}")
        else:
            raise Exception(f"Error getting positions: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")