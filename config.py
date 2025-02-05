from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # RaidenX config
    RAIDENX_API_COMMON_URL = os.getenv('RAIDENX_API_COMMON_URL', 'https://api.dextrade.bot')
    RAIDENX_API_INSIGHT_URL = os.getenv('RAIDENX_API_INSIGHT_URL', 'https://api-insight.dextrade.bot')
    RAIDENX_API_ORDERS_URL = os.getenv('RAIDENX_API_ORDERS_URL', 'https://api-orders.dextrade.bot')
    RAIDENX_API_WALLETS_URL = os.getenv('RAIDENX_API_WALLETS_URL', 'https://api-wallets.dextrade.bot')

    @property
    def RAIDENX_CONFIG(self):
        return {
            'api_common_url': self.RAIDENX_API_COMMON_URL,
            'api_insight_url': self.RAIDENX_API_INSIGHT_URL,
            'api_orders_url': self.RAIDENX_API_ORDERS_URL,
            'api_wallets_url': self.RAIDENX_API_WALLETS_URL
        }
    
    # AI Agent BE config
    AGENTFAI_API_URL = os.getenv('AGENTFAI_API_URL', 'https://api-agentfai.dextrade.bot')
    AGENTFAI_API_KEY = os.getenv('AGENTFAI_API_KEY', 'your_api_key_here')

    @property
    def AGENTFAI_CONFIG(self):
        return {
            'api_url': self.AGENTFAI_API_URL,
            'api_key': self.AGENTFAI_API_KEY
        }

# Create a config instance
config = Config()
