from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import Dict

load_dotenv()

@dataclass
class RaidenSettings:
    """Settings for RaidenX API endpoints"""
    api_common_url: str = os.getenv('RAIDENX_API_COMMON_URL', 'https://api.dextrade.bot')
    api_insight_url: str = os.getenv('RAIDENX_API_INSIGHT_URL', 'https://api-insight.dextrade.bot')
    api_orders_url: str = os.getenv('RAIDENX_API_ORDERS_URL', 'https://api-orders.dextrade.bot')
    api_wallets_url: str = os.getenv('RAIDENX_API_WALLETS_URL', 'https://api-wallets.dextrade.bot')

    def get_config(self) -> Dict[str, str]:
        """Returns RaidenX configuration as dictionary"""
        return {
            'api_common_url': self.api_common_url,
            'api_insight_url': self.api_insight_url,
            'api_orders_url': self.api_orders_url,
            'api_wallets_url': self.api_wallets_url
        }

@dataclass
class AgentSettings:
    """Settings for AI Agent backend"""
    api_url: str = os.getenv('AGENTFAI_API_URL', 'https://api-agentfai.dextrade.bot')
    api_key: str = os.getenv('AGENTFAI_API_KEY', 'your_api_key_here')

    def get_config(self) -> Dict[str, str]:
        """Returns Agent configuration as dictionary"""
        return {
            'api_url': self.api_url,
            'api_key': self.api_key
        }

class Settings:
    """Main application settings"""
    def __init__(self):
        self.raiden = RaidenSettings()
        self.agent = AgentSettings()

# Create a singleton settings instance
settings = Settings()
