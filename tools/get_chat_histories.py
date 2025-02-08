import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from config import settings

import json
import os
from typing import List
from llama_index.core.llms import ChatMessage, MessageRole

def fetch_thread_messages(thread_id: str) -> dict:
    """
    Get chat histories for a specific thread
    
    Args:
        thread_id (str): Thread ID
        
    Returns:
        dict: Chat histories sorted by creation time

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
        url = f"{settings.agent.api_url}/api/v1/backend/thread/{thread_id}/messages"
        headers = {
            "X-API-KEY": settings.agent.api_key
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if 'docs' in data:
            data['docs'] = sorted(data['docs'], key=lambda x: x['createdAt'])
            
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"API connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting chat histories: {str(e)}")
    
    
# def convert_dict_to_chat_messages(
#     chat_dicts: List[dict[str, str]],
#     ) -> List[ChatMessage]:
#     """
#     Convert a list of dictionaries to a list of ChatMessage objects.

#     Args:
#         chat_dicts (List[Dict[str, str]]): A list of dictionaries with "role" and "content" keys.

#     Returns:
#         List[ChatMessage]: A list of ChatMessage objects.
#     """
#     chat_messages = []
#     for chat_dict in chat_dicts:
#         # Ensure the dictionary has the required keys
#         if "role" not in chat_dict or "content" not in chat_dict:
#             raise ValueError("Each dictionary must contain 'role' and 'content' keys.")

#         # Normalize the role to match the MessageRole class
#         role = chat_dict["role"].lower()
#         if role not in [MessageRole.ASSISTANT, MessageRole.USER]:
#             raise ValueError(
#                 f"Invalid role: {role}. Role must be 'assistant' or 'user'."
#             )

#         # Create a ChatMessage object and add it to the list
#         chat_message = ChatMessage(role=role, content=chat_dict["content"])
#         chat_messages.append(chat_message)

#     return chat_messages   
    
    
# messages = fetch_thread_messages("67a34762cb3fce146d63ba27")
# print(messages)
# chat_history_message = convert_dict_to_chat_messages(messages)
# print(chat_history_message)