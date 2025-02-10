import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from typing import Dict, Any, Optional, Tuple, Union
from config import settings

def scan_token(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about the top trading pair for a specific token
    
    Args:
        token_address (str): Token address
        
    Returns:
        str: Formatted pair information or None if error occurs
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

        # Extract token info
        base_token = data.get("tokenBase", {})
        token_name = base_token.get("name", "")
        token_symbol = base_token.get("symbol", "")
        token_address = base_token.get("address", "")
        
        # Extract DEX info
        dex = data.get("dex", {})
        dex_name = dex.get("name", "")
        
        # Calculate age
        created_at = data.get("createdAt", "")
        # TODO: Add age calculation logic
        age = "6d,10h,52m"  # Placeholder
        
        # Extract stats
        stats = data.get("stats", {})
        percent = stats.get("percent", {})
        volume = stats.get("volume", {})
        buy_txn = stats.get("buyTxn", {})
        sell_txn = stats.get("sellTxn", {})
        
        # Format the output
        output = f"**{token_name} ({token_symbol})**\n"
        output += f"`{token_address}`\n\n"
        
        output += f"**Platform:** {dex_name} | **Age:** {age}\n"
        
        # Convert string values to float for formatting
        mcap = float(data.get('marketCapUsd', '0'))
        liq = float(data.get('liquidityUsd', '0'))
        price = float(base_token.get('priceUsd', '0'))
        
        output += f"**MCap:** ${mcap/1000:.2f}K | "
        output += f"**Liq:** ${liq:.2f}K\n"
        output += f"**Current Price:** ${price:.4f}\n\n"
        
        # Format time-based stats in table format
        output += "| Time | Price | Volume | Buy/Sell |\n"
        output += "|------|--------|---------|----------|\n"
        periods = ["5m", "1h", "6h", "24h"]
        for period in periods:
            price_change = float(percent.get(period, 0))
            vol = float(volume.get(period, 0))
            buys = int(buy_txn.get(period, 0))
            sells = int(sell_txn.get(period, 0))
            
            output += f"| {period.upper()} | {price_change:>6.2f}% | ${vol/1000:.2f}K | {buys}/{sells} |\n"
        
        return output
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top pair: {str(e)}")
        return None

# # Example usage:
# if __name__ == "__main__":
#     sample_token = "0x9467f809de80564fa198b2c9a27557bf4ffcf1aa506f28547661b96d8f84a1dc::prez::PREZ"
    
#     result = fetch_top_pair(sample_token)
#     if result:
#         print(result)
#     else:
#         print("Failed to fetch pair information")