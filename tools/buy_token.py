import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
from config import settings

load_dotenv()

checker = OrderChecker()

def buy_token(token_address: str, amount: float, wallet_address: str, jwt_token: str) -> str:
    """
    Buy a token with a specified amount of SUI from a user's wallet

    Args:
        token_address (str): Token contract address
        amount (float): Amount in SUI to spend
        wallet_address (str): User's wallet address
        jwt_token (str): Authorization token
        
    Returns:
        str: Transaction result message containing:
            - Amount spent in SUI
            - Amount of tokens received
            - Destination wallet address
            - Transaction explorer URL
            
    Raises:
        RequestException: If API request fails
        Exception: If any other error occurs during the purchase
    """
    try:
        result = fetch_top_pair(token_address)
        if result is None:
            return f"Failed to fetch top pair information for {token_address}. Please try again later."
            
        network, pair_id = result  # Chỉ unpack khi chắc chắn result không phải None
        if not pair_id:
            return f"No trading pair found for token {token_address}"
        
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
            f"{settings.raiden.api_orders_url}/api/v1/sui/orders/quick-buy",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        
        result = response.json()
        if not result:
            return "⚠️ Failed to purchase: Insufficient liquidity in this pair. Please try another token or wait for more liquidity."
            
        order_id = result[0]["order"]["id"]
        
        status = checker.check_order_status(order_id, jwt_token)
        
        print(f"status-buy-token: {status}")
        
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
#     print(buy_token("2104920255", "hungdv", "hungdv", "0x1974ea7ea3bd5290f7f9fdf69e9f8aac766a55a3783d18431a7a1358418eb9f4::ppei::PPEI", 0.003, "0xea1bc45a51e0051b6a7b53c3ce4f0a45d416b985042ff51f73ca8155452daf7f"))