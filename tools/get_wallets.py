import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from auth.jwt_generator import get_jwt
from tools.utils import json_to_dict
import random
from config import settings


def get_wallet_balance(userId: str, userName: str = "", displayName: str = "") -> dict:
    """
    Get wallet balance and information from user's wallet

    Args:
        userId (str): User's ID
        userName (str, optional): Username. Defaults to empty string
        displayName (str, optional): Display name. Defaults to empty string
        
    Returns:
        dict: Wallet information containing:
            - address (str): Wallet address
            - balance (float): Current wallet balance
            - network (str): Network identifier
            
    Raises:
        RequestException: If API request fails
        Exception: If wallet data cannot be retrieved
    """

    jwt_token = get_jwt(userId, userName, displayName)
    
    url = f"{settings.raiden.api_wallets_url}/api/v1/sui/user-wallets"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.get(url, headers=headers)
    
    wallet_data = {}
    
    if response.status_code == 200:
        wallets = response.json()
        wallet_data['address'] = wallets[0]['address']
        wallet_data['balance'] = wallets[0]['balance']
        wallet_data['network'] = wallets[0]['network']
        return wallet_data

    else:
        raise Exception(f"Error fetching wallets: {response.status_code} - {response.text}")
    