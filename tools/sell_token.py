import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import Tool
import requests
from auth.jwt_generator import get_jwt

from tools.utils import json_to_dict

# @json_to_dict
def sell_token(userId: str, userName: str, displayName: str, token_address: str, amount: float) -> str:
    """
    Lấy thông tin positions của một token cụ thể trong các ví
    
    Args:
        userId (str): ID của user
        userName (str): Tên user
        displayName (str): Tên hiển thị
        token_address (str): Địa chỉ của token cần buy
        amount: Amount in sui, percentage
        
    Returns:
        dict: Thông tin positions của token
    """
    jwt_token = get_jwt(userId, userName, displayName)
    if not (0 <= amount <= 100):
        return f"Error: Amount must be a percentage between 0 and 100. Received: {amount}"
    purchase_message = (
        f"User {userName} (ID: {userId}, Display Name: {displayName}) "
        f"successfully bought {amount}% of token at address {token_address}."
        f"Thank you for using our service. Feature current on Beta."
    )
    return purchase_message 
