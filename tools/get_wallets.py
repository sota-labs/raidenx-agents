import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
from tools.utils import json_to_dict

# @json_to_dict
def get_wallets(userId: str, userName: str = "", displayName: str = "") -> dict:
    jwt_token = get_jwt(userId, userName, displayName)
    
    url = "https://api-wallets.dextrade.bot/api/v1/sui/user-wallets"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching wallets: {response.status_code} - {response.text}")
    