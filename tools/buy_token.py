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
from tools.get_top_pair import fetch_top_pair
from tools.check_order import OrderChecker
from config import config

load_dotenv()

checker = OrderChecker()

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
    try:
        jwt_token = get_jwt(userId, userName, displayName)
        
        network, pair_id = fetch_top_pair(token_address)
        if network is None or pair_id is None:
            return f"Failed to fetch top pair information for {token_address}. Please try again later."
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "buyAmount": str(amount),
            "tokenAddress": token_address,
            "orderSetting": {
                "priorityFee": "0",
                "slippage": 40
            },
            "pairId": pair_id,
            "wallets": [wallet_address]
        }
        
        response = requests.post(
            f"{config.RAIDENX_CONFIG['api_orders_url']}/api/v1/sui/orders/quick-buy",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        if not result:
            return "⚠️ Failed to purchase: Insufficient liquidity in this pair. Please try another token or wait for more liquidity."
            
        order_id = result[0]["order"]["id"]
        status = asyncio.run(checker.check_order_status(order_id, jwt_token))
        
        explorer_url = f"https://suivision.xyz/txblock/{status['hash']}"
        message = (
            f"✅ I've successfully purchased the token for you:\n"
            f"💰 Spent: {status['amountIn']} SUI\n"
            f"📈 Received: {status['amountOut']} tokens\n" 
            f"👛 To wallet: {wallet_address}\n"
            f"🔍 Transaction: {explorer_url}"
        )
        
        # messenger = TelegramMessenger()
        # asyncio.run(messenger.send_message(
        #     f"🟢 Buy Alert: User {displayName} ({userName}) has purchased {token_address} token for {amount} SUI"
        # ))
        
        return message
        
    except requests.exceptions.RequestException as e:
        return f"Error occurred while making the purchase: {str(e)}"


# if __name__ == "__main__":
#     print(buy_token("2104920255", "hungdv", "hungdv", "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d::atrump::ATRUMP", 1, "0xbf22770b3d5f08b5a2942f7071d9b0446aa80518d257d9fb55f6b08a3ab28f8d"))