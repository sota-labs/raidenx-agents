import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import time
from typing import Dict
from config import settings

class OrderChecker:
    def __init__(self):
        self.base_url = f"{settings.raiden.api_orders_url}/api/v1/sui/orders"
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1

    def get_order_details(self, result: Dict) -> Dict:
        """
        Extract relevant order details from the response
        """
        return {
            "status": result.get("status", "pending"),
            "amountIn": result.get("amountIn"),
            "amountOut": result.get("amountOut"),
            "hash": result.get("hash", ""),
            "sellPercent": result.get("sellPercent"),
            "error": result.get("error", "")
        }

    def check_order_status(
        self, 
        order_id: str,
        jwt_token: str
    ) -> Dict:
        """
        Check the status of an order with retries
        Args:
            order_id: The ID of the order to check
            jwt_token: JWT token for authentication
        Returns:
            dict: Order details including status, amounts, hash
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                url = f"{self.base_url}/{order_id}"
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {jwt_token}"
                }
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                if not result:
                    return {"status": "error", "error": "Empty response from server"}
                    
                order_details = self.get_order_details(result)
                
                if order_details["status"] == "success":
                    return order_details
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return order_details
                
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return {"error": f"Failed to get order status: {str(e)}"}

# Example usage
# if __name__ == "__main__":
#     checker = OrderChecker()
#     jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIyMTA0OTIwMjU1IiwidXNlck5hbWUiOiJoYXJyeWRhbmcxIiwiZGlzcGxheU5hbWUiOiJIYXJyeSBEYW5nIiwiaWFwIjpudWxsLCJpYXQiOjE3Mzg3MzgwOTYsImV4cCI6MTc0MTMzMDA5Nn0.e13mInVvyZlhJMrHH7y6OF7trNZ18KbCCEojrTPK1LM"
    
#     status = checker.check_order_status(
#         "67a33734119889f149a5e2bc",
#         jwt_token
#     )
#     print("Order Details:", status) 