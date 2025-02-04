import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
from tools.utils import json_to_dict
import random

def get_wallet_balance(userId: str, userName: str = "", displayName: str = "") -> dict:
    jwt_token = get_jwt(userId, userName, displayName)
    
    url = "https://api-wallets.dextrade.bot/api/v1/sui/user-wallets"
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
    