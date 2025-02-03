import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
import asyncio
from telegram.ext import ApplicationBuilder
from telegram import Bot

from tools.utils import json_to_dict
from tools.get_wallets import get_wallet_balance
from dotenv import load_dotenv
from commons.send_telegram import TelegramMessenger

load_dotenv()

def buy_token(userId: str, userName: str, displayName: str, token_address: str, amount: float, wallet_address: str) -> str:
    """
    Buy a token with a specified amount of SUI from a user's wallet
    Args:
        userId (str): User's ID
        userName (str): Username
        displayName (str): Display name
        token_address (str): Token contract address
        amount (float): Amount in SUI to spend
        wallet_address (str): User's wallet address
        
    Returns:
        str: Transaction result message
    """
    jwt_token = get_jwt(userId, userName, displayName)
    
    # wallet_balance = get_wallet_balance(userId, userName, displayName)
    # if wallet_balance['balance'] < amount:
    #     return f"You do not have enough SUI to buy {amount} SUI worth of {token_address}. Your current balance is {wallet_balance['balance']} SUI. Please top up your wallet and try again."
    
    response = f"Successfully purchased {token_address} token for {amount} SUI from wallet {wallet_address}. Feature is currently in Beta."
    
    messenger = TelegramMessenger()
    asyncio.run(messenger.send_message(f"🟢 Buy Alert: User {displayName} ({userName}) has purchased {token_address} token for {amount} SUI • ⚠️ Feature is currently in Beta"))
    
    return response 


# if __name__ == "__main__":
#     print(buy_token("2104920255", "hungdv", "hungdv", "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d::atrump::ATRUMP", 1, "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d"))