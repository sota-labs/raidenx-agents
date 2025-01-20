import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from auth.jwt_generator import get_jwt
from langchain.agents import Tool
from tools.utils import json_to_dict

@json_to_dict
def get_wallets(userId: str, userName: str = None, displayName: str = None) -> dict:
    # Tạo JWT token
    jwt_token = get_jwt(userId, userName, displayName)
    
    # Cấu hình URL và headers
    url = "https://api-wallets.dextrade.bot/api/v1/sui/user-wallets"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    # Gửi GET request
    response = requests.get(url, headers=headers)
    
    # Kiểm tra response status
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching wallets: {response.status_code} - {response.text}")
    
    
get_wallets_tool = Tool(
    name="Get Wallet of user",
    func=get_wallets,
    description=(
        "Useful for retrieving wallet information associated with a user."
        """Input args: userId (str): The user's unique identifier.
        userName (str): The user's username.
        displayName (str): The user's display name."""
        "Use this tool in crypto applications to fetch wallet details for analysis, tracking, or integration."
    )
)

# # Example usage
# if __name__ == "__main__":
#     try:
#         # Ví dụ với một token address
#         token_address = "0xea1bc45a51e0051b6a7b53c3ce4f0a45d416b985042ff51f73ca8155452daf7f"
#         wallets = get_wallets("2104920255", "harrydang1", "Harry Dang")
#         print(wallets[0])
#         print(f"Wallets List:")
#         print(wallets)
#     except Exception as e:
#         print(f"Error: {e}") 