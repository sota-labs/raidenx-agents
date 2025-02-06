import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import asyncio
from auth.jwt_generator import get_jwt
from commons.send_telegram import TelegramMessenger
from tools.utils import json_to_dict
from tools.get_top_pair import fetch_top_pair
from tools.check_order import OrderChecker
from config import settings

checker = OrderChecker()

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
        str: Transaction result message containing:
            - Amount of tokens sold
            - Amount of SUI received
            - Sell percentage
            - Source wallet address
            - Transaction explorer URL
            
    Raises:
        RequestException: If API request fails
        ValueError: If percent is not between 0 and 100
        Exception: If sale operation fails with error message
    """
    try:
        jwt_token = get_jwt(userId, userName, displayName)
        percent = float(percent)
        if not (0 <= percent <= 100):
            return f"Error: Percent must be a percentage between 0 and 100. Received: {percent}"
        
        network, pair_id = fetch_top_pair(token_address)
        if network is None or pair_id is None:
            return f"Failed to fetch top pair information for {token_address}. Please try again later."
        
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "orderSetting": {
                "priorityFee": "0",
                "slippage": 40
            },
            "pairId": pair_id,
            "tokenAddress": token_address,
            "sellPercent": float(percent),
            "wallets": [wallet_address]
        }
        
        response = requests.post(
            f"{settings.raiden.api_orders_url}/api/v1/sui/orders/quick-sell",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        if not result:
            return "⚠️ Failed to sell: Insufficient liquidity in this pair. Please try another token or wait for more liquidity."
            
        order_id = result[0]["order"]["id"]
        
        status = checker.check_order_status(order_id, jwt_token)
        
        explorer_url = f"https://suivision.xyz/txblock/{status['hash']}"
        message = (
            f"✅ Sale successful:\n"
            f"💰 Sold: {status['amountIn']} tokens\n"
            f"📈 Received: {status['amountOut']} SUI\n"
            f"📊 Percentage: {status['sellPercent']}%\n"
            f"👛 From wallet: {wallet_address}\n"
            f"🔍 Transaction: {explorer_url}"
        )
        
        # messenger = TelegramMessenger()
        # asyncio.run(messenger.send_message(
        #     f"🔴 Sell Alert: User {displayName} ({userName}) has sold {percent}% of {token_address} token"
        # ))
        
        return message
        
    except requests.exceptions.RequestException as e:
        return f"Error occurred while making the sale: {str(e)}"


# if __name__ == "__main__":
#     print(sell_token("2104920255", "hungdv", "hungdv", "0x1974ea7ea3bd5290f7f9fdf69e9f8aac766a55a3783d18431a7a1358418eb9f4::ppei::PPEI", 10, "0xea1bc45a51e0051b6a7b53c3ce4f0a45d416b985042ff51f73ca8155452daf7f"))