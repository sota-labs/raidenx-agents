import requests
from config import config

def get_chat_histories(thread_id: str) -> dict:
    """
    Get chat histories for a specific thread
    
    Args:
        thread_id (str): Thread ID
        
    Returns:
        dict: Chat histories

    The API returns a paginated list of chat messages with the following structure:
    {
        "totalDocs": int,      # Total number of messages
        "totalPages": int,     # Total number of pages
        "limit": int,          # Number of messages per page
        "page": int,           # Current page number
        "docs": [              # Array of message objects
            {
                "id": str,         # Message ID
                "agentId": str,    # ID of the agent
                "threadId": str,   # Thread ID
                "question": str,   # User's question
                "answer": str,     # Agent's response
                "createdAt": int,  # Message creation timestamp (seconds)
                "updatedAt": int   # Message update timestamp (seconds)
            }
        ]
    }
    """
    try:
        url = f"{config.AGENTFAI_CONFIG['api_url']}/api/v1/backend/thread/{thread_id}/messages"
        headers = {
            "X-API-KEY": config.AGENTFAI_CONFIG['api_key']
        }
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting chat histories: {str(e)}")
