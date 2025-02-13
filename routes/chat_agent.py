from fastapi import FastAPI, HTTPException, APIRouter, Path, Query, Body, Depends, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio
import aiohttp

from auth.authorization import verify_token

import os
from dotenv import load_dotenv
from utils.chat_session import (
    load_chat_history,
    save_chat_history,
    convert_dict_to_chat_messages,
    escape_markdown_v2,
)
from agents import react_chat, llm
from tools.get_chat_histories import fetch_thread_messages
from config.settings import settings

router = APIRouter()

class AgentRequest(BaseModel):
    content: str
    message_id: str
    thread_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "hi",
                "message_id": "msg_123",
                "thread_id": "thread_123"
            }
        }

class AgentResponse(BaseModel):
    """Response model for agent interactions.
    
    Attributes:
        message (str): The response message from the agent
        timestamp (str): ISO format timestamp of the response
        user (str): Username of the requesting user
        chat_id (str): Unique identifier for the chat session
            Example:
            {
                "token_address": "0xcce8036f36aefd05105c46c7245f3ba6203dde5a624c8319f120925903b541b7::elon::ELON",
                "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "amount": "10"
            }
    """
    message: str
    timestamp: str
    user: str
    chat_id: str
   

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "message": "Would you like to confirm buying 10 SUI of ELON token at address: 0xcce8036f36aefd05105c46c7245f3ba6203dde5a624c8319f120925903b541b7::elon::ELON?",
                "timestamp": "2024-03-20 10:30:45",
                "user": "john_doe",
                "chat_id": "user123",
            }
        }

class WebhookResponse(BaseModel):
    """Response model for webhook confirmation
    
    Attributes:
        status (str): Status of the webhook request
        message_id (str): ID of the message being processed
        thread_id (str): ID of the thread
        action (str, optional): Action được trả về từ bot
    """
    status: str
    message_id: str
    thread_id: str
    action: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "processing",
                "message_id": "msg_123",
                "thread_id": "thread_123",
                "action": "buy_token"
            }
        }

class WebhookTriggerRequest(BaseModel):
    """Request model for webhook trigger
    
    Attributes:
        answer (str): Response message from backend
        messageId (str): ID of the message
    """
    answer: str
    messageId: str
    action: str | None = None

class WebhookTriggerResponse(BaseModel):
    """Response model for webhook trigger
    
    Attributes:
        status (str): Status of the operation
        messageId (str): ID of the message processed
    """
    status: str
    messageId: str

VALID_ACTIONS = {"buy_token", "sell_token"}

@router.post("/threads/messages/sync", response_model=AgentResponse)
async def create_message_sync(
    request: AgentRequest,
    session: dict = Depends(verify_token),
    authorization: str = Header(None, description="Bearer token")
):    
    try:
        jwt_token = authorization.replace("Bearer ", "") if authorization else None
        
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")
            
        user = session["userName"]
        user_message = request.content
        message_id = request.message_id
        thread_id = request.thread_id
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            chat_history = load_chat_history()
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to load chat history")
            
        chat_id = thread_id
        try:
            messages = fetch_thread_messages(thread_id)
        except Exception as e:
            print(f"Error fetching thread messages: {str(e)}")
            messages = []

        if chat_id not in chat_history:
            chat_history[chat_id] = []

        chat_history[chat_id].append({
            "role": "user", 
            "content": user_message, 
            "time": current_time,
            "message_id": message_id,
            "thread_id": thread_id
        })
        
        last_five_messages = messages[-10:] if messages else []
        chat_history_message = convert_dict_to_chat_messages(last_five_messages)
        
        try:
            bot_response_dict = react_chat(
                query=user_message,
                llm=llm,
                chat_history=chat_history_message,
                jwt_token=jwt_token
            )
            
            if isinstance(bot_response_dict, dict):
                bot_response = bot_response_dict.get("response", "")
            else:
                bot_response = str(bot_response_dict)
            
        except Exception as e:
            print(f"Error in react_chat: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
        
        chat_history[chat_id].append({
            "role": "assistant", 
            "content": bot_response,
            "time": current_time,
            "message_id": message_id,
            "thread_id": thread_id
        })

        if len(chat_history[chat_id]) > 20:
            chat_history[chat_id] = chat_history[chat_id][-20:]

        try:
            save_chat_history(chat_history)
        except Exception as e:
            print(f"Warning: Failed to save chat history: {str(e)}")
            
        return AgentResponse(
            message=bot_response,
            timestamp=current_time,
            user=user,
            chat_id=chat_id
        )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/threads/messages", response_model=WebhookResponse)
async def create_message_async(
    request: AgentRequest,
    session: dict = Depends(verify_token),
    authorization: str = Header(None, description="Bearer token")
):    
    task = asyncio.create_task(
        process_message_webhook(
            request=request,
            session=session,
            jwt_token=authorization.replace("Bearer ", "") if authorization else None,
            webhook_url=f"{settings.agent.api_url}/api/v1/backend/message/agent-webhook-trigger"
        )
    )
    
    return WebhookResponse(
        status="processing",
        message_id=request.message_id,
        thread_id=request.thread_id,
        action=None 
    )

async def process_message_webhook(
    request: AgentRequest,
    session: dict,
    jwt_token: str,
    webhook_url: str
):
    try:
        
        user = session["userName"]
        user_message = request.content
        message_id = request.message_id
        thread_id = request.thread_id
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history = load_chat_history()
        
        chat_id = thread_id
        messages = fetch_thread_messages(thread_id)
        
        
        print(f"User Message: {user_message}")
        print(f"Chat History: {messages}")
        print(f"thread_id: {thread_id}")
        print(f"message_id: {message_id}")

        if chat_id not in chat_history:
            chat_history[chat_id] = []

        chat_history[chat_id].append({
            "role": "user", 
            "content": user_message, 
            "time": current_time,
            "message_id": message_id,
            "thread_id": thread_id
        })
        # last_five_messages = chat_history[chat_id][-10:]
        
        last_five_messages = messages[-10:]

        chat_history_message = convert_dict_to_chat_messages(last_five_messages)
        
        bot_response_dict = react_chat(
            query=user_message,
            llm=llm,
            chat_history=chat_history_message,
            jwt_token=jwt_token
        )

        bot_response = bot_response_dict["response"]
        action = bot_response_dict.get("action")
        action_response = action if action in VALID_ACTIONS else None
        
        # chat_history[chat_id].append({
        #     "role": "assistant", 
        #     "content": bot_response,
        #     "time": current_time,
        #     "message_id": message_id,
        #     "thread_id": thread_id
        # })

        # if len(chat_history[chat_id]) > 20:
        #     chat_history[chat_id] = chat_history[chat_id][-20:]

        # save_chat_history(chat_history)
        
        webhook_response = WebhookTriggerRequest(
            answer=bot_response,
            messageId=message_id,
            action=action_response
        )
        
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                webhook_url,
                json=webhook_response.dict(),
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": settings.agent.api_key
                }
            )
            response_text = await response.text()
            print(f"Webhook Response: Status={response.status}, Body={response_text}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        error_response = {
            "error": str(e),
            "message_id": message_id,
            "thread_id": thread_id
        }
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                webhook_url,
                json=error_response,
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": settings.agent.api_key
                }
            )
            response_text = await response.text()
            print(f"Error Webhook Response: Status={response.status}, Body={response_text}")