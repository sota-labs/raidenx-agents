import requests
from typing import Dict, Any, Optional, Tuple, Union
from config import config

def fetch_top_pair(token_address: str) -> Union[Tuple[str, str], Dict[str, str]]:
    """
    Fetch network and pairId information of top pair from Dextrade API
    
    Args:
        token_address (str): Token address to query
        
    Returns:
        Union[Tuple[str, str], Dict[str, str]]: 
            - Success: Tuple containing (network, pairId)
            - Error: Dict with error information {'error': error_message}
    """
    try:
        url = f"{config.RAIDENX_CONFIG['api_common_url']}/api/v1/sui/tokens/{token_address}/top-pair"
        response = requests.get(url)
        
        # Handle 502 Bad Gateway - Invalid token address
        if response.status_code == 502:
            return {'error': 'Invalid token address'}
            
        response.raise_for_status()  # Raise exception cho các status code lỗi
        
        data = response.json()
        # Chỉ trả về network và pairId
        return data['network'], data['pairId']
        
    except requests.RequestException as e:
        return {'error': f'API request error: {str(e)}'}
    except (ValueError, KeyError) as e:
        return {'error': f'Data processing error: {str(e)}'}

# Example usage:
# if __name__ == "__main__":
#     # Token address mẫu
#     sample_token = "0x058af7f23d1341e30a2138053f3bb1e6bb5c5be4a60b56e6e81814364b8425d0::impakaia::IMPAKAIA"
    
#     result = fetch_top_pair(sample_token)
#     if isinstance(result, tuple):
#         network, pair_id = result
#         print(f"Network: {network}")
#         print(f"Pair ID: {pair_id}")
#     else:
#         print(f"Error: {result['error']}")