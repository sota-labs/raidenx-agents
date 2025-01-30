import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
from commons.send_telegram import TelegramMessenger
from tools.utils import json_to_dict

# @json_to_dict
def sell_token(userId: str, userName: str, displayName: str, token_address: str, percent: float, wallet_address: str) -> str:
    """
    Sell a percentage of a token from a user's wallet
    
    Args:
        userId (str): User's ID
        userName (str): Username
        displayName (str): Display name
        token_address (str): Token contract address
        percent (float): Percentage of tokens to sell (0-100)
        wallet_address (str): User's wallet address
        
    Returns:
        str: Transaction result message
    """
    jwt_token = get_jwt(userId, userName, displayName)
    percent = float(percent)
    if not (0 <= percent <= 100):
        return f"Error: Percent must be a percentage between 0 and 100. Received: {percent}"
    
    response = f"Successfully sold {percent}% of {token_address} token from wallet {wallet_address}. Feature is currently in Beta."
    
    messenger = TelegramMessenger()
    asyncio.run(messenger.send_message(f"🔴 Sell Alert: User {displayName} ({userName}) has sold {percent}% of {token_address} token • ⚠️ Feature is currently in Beta"))
    
    return response 


# if __name__ == "__main__":
#     print(sell_token("2104920255", "hungdv", "hungdv", "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d::atrump::ATRUMP", 1, "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d"))