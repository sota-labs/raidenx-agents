import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt

from tools.utils import json_to_dict

# @json_to_dict
def get_positions_by_token(userId: str, userName: str, displayName: str, token_address: str) -> dict:
    """
    Lấy thông tin positions của một token cụ thể trong các ví
    
    Args:
        userId (str): ID của user
        userName (str): Tên user
        displayName (str): Tên hiển thị
        token_address (str): Địa chỉ của token cần kiểm tra
        
    Returns:
        dict: Thông tin positions của token
    """
    jwt_token = get_jwt(userId, userName, displayName)
    
    url = f"https://api-insight.dextrade.bot/sui/api/v1/my/positions/{token_address}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()['docs'][0]
        token_data = {}
        token_data['symbol'] = response_data['token']['symbol']
        token_data['name'] = response_data['token']['name']
        token_data['address'] = response_data['token']['address']
        token_data['balance'] = response_data['balance']
        token_data['wallet_address'] = response_data['walletName']
        return [token_data]
    else:
        raise Exception(f"Error fetching positions: {response.status_code} - {response.text}")