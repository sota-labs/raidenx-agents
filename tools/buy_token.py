import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt

from tools.utils import json_to_dict

# @json_to_dict
def buy_token(userId: str, userName: str, displayName: str, token_address: str, amount: float) -> str:
    """
    Lấy thông tin positions của một token cụ thể trong các ví
    
    Args:
        userId (str): ID của user
        userName (str): Tên user
        displayName (str): Tên hiển thị
        token_address (str): Địa chỉ của token cần buy
        amount: Amount in sui
        
    Returns:
        dict: Thông tin positions của token
    """
    jwt_token = get_jwt(userId, userName, displayName)
    
    response = f"Buy token {token_address} with amount successfully!!! Feature current in Beta"
    return response 
