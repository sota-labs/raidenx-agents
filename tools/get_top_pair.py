import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from typing import Dict, Any, Optional, Tuple, Union
from config import settings

def fetch_top_pair(token_address: str):
    """
    Lấy thông tin về cặp giao dịch hàng đầu cho một token cụ thể
    
    Args:
        token_address (str): Địa chỉ của token
        
    Returns:
        tuple: (network, pair_id) hoặc None nếu có lỗi
    """
    try:
        url = f"{settings.raiden.api_common_url}/api/v1/sui/tokens/{token_address}/top-pair"
        
        response = requests.get(url)
        
        if response.status_code == 404:
            print(f"Token not found: {token_address}")
            return None
        elif response.status_code == 502:
            print(f"Invalid token address: {token_address}")
            return None
            
        response.raise_for_status()
        
        data = response.json()
        if not data:
            print(f"No data returned for token {token_address}")
            return None
        
        network = data.get("network")
        pair_id = data.get("pairId")
        
        if network is None or pair_id is None:
            print(f"Missing network or pair_id in response: {data}")
            return None
            
        return (network, pair_id)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top pair: {str(e)}")
        return None

# Example usage:
# if __name__ == "__main__":
#     sample_token = "0x9467f809de80564fa198b2c9a27557bf4ffcf1aa506f28547661b96d8f84a1dc::prez::PREZ"
    
#     result = fetch_top_pair(sample_token)
#     if isinstance(result, tuple):
#         network, pair_id = result
#         print(f"Network: {network}")
#         print(f"Pair ID: {pair_id}")
#     else:
#         print(f"Error: {result['error']}")