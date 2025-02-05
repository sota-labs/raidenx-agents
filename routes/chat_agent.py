from fastapi import FastAPI, HTTPException, APIRouter, Path, Query, Body, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio

from auth.authorization import verify_token

import os
from dotenv import load_dotenv
from utils.chat_session import (
    load_chat_history,
    save_chat_history,
    convert_dict_to_chat_messages,
    escape_markdown_v2,
)
from agents import react_chat, llm, react_chat_stream

router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "I want to buy 10 SUI of ELON token"
            }
        }

class AgentResponse(BaseModel):
    """Response model for agent interactions.
    
    Attributes:
        message (str): The response message from the agent
        timestamp (str): ISO format timestamp of the response
        user (str): Username of the requesting user
        chat_id (str): Unique identifier for the chat session
        action (str): Type of action to be performed (e.g., "buy", "sell", "none")
        action_input (dict): Parameters for the specified action
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
    action: str = "none"
    action_input: dict = {}

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "message": "Would you like to confirm buying 10 SUI of ELON token at address: 0xcce8036f36aefd05105c46c7245f3ba6203dde5a624c8319f120925903b541b7::elon::ELON?",
                "timestamp": "2024-03-20 10:30:45",
                "user": "john_doe",
                "chat_id": "user123",
                "action": "buy",
                "action_input": {
                    "token_address": "0xcce8036f36aefd05105c46c7245f3ba6203dde5a624c8319f120925903b541b7::elon::ELON",
                    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                    "amount": "10"
                }
            }
        }

@router.post("/agent-response", response_model=AgentResponse)
async def generate_bot_response(request: AgentRequest,
                                session: dict = Depends(verify_token)
    ):
    
    chat_id = session["userId"]
    user = session["userName"]
    
    user_message = request.query
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history = load_chat_history()

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append(
        {"role": "user", "content": user_message, "time": current_time}
    )
    last_five_messages = chat_history[chat_id][-10:]

    chat_history_message = convert_dict_to_chat_messages(last_five_messages)
    
    bot_response = react_chat(
        query=user_message,
        llm=llm,
        chat_history=chat_history_message,
        userId=chat_id,
        userName=user,
        displayName=user,
    )
    
    chat_history[chat_id].append(
        {"role": "assistant", "content": bot_response, "time": current_time}
    )

    if len(chat_history[chat_id]) > 20:
        chat_history[chat_id] = chat_history[chat_id][-20:]

    save_chat_history(chat_history)
        
    return AgentResponse(
        message=bot_response,
        timestamp=current_time,
        user=user,
        chat_id=chat_id,
        action="none",  # Using "none" as default action
        action_input={}
    )

@router.post("/agent-stream")
async def generate_bot_response_stream(
    request: AgentRequest,
    session: dict = Depends(verify_token)
):
    chat_id = session["userId"]
    user = session["userName"]
    
    user_message = request.query
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history = load_chat_history()

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append(
        {"role": "user", "content": user_message, "time": current_time}
    )
    last_five_messages = chat_history[chat_id][-10:]
    chat_history_message = convert_dict_to_chat_messages(last_five_messages)
    
    async def process_stream():
        full_response = ""
        buffer = ""
        
        async for token in react_chat_stream(
            query=user_message,
            llm=llm,
            chat_history=chat_history_message,
            userId=chat_id,
            userName=user,
            displayName=user,
        ):
            full_response += token
            buffer += token
            
            while buffer:
                char = buffer[0]
                buffer = buffer[1:]
                yield f"data: {char}\n\n"
                await asyncio.sleep(0.01)  # 10ms delay
        
        # Send [DONE] signal
        yield "data: [DONE]\n\n"
        
        # Save the complete response to chat history
        chat_history[chat_id].append(
            {"role": "assistant", "content": full_response, "time": current_time}
        )

        if len(chat_history[chat_id]) > 20:
            chat_history[chat_id] = chat_history[chat_id][-20:]

        save_chat_history(chat_history)
    
    return StreamingResponse(
        process_stream(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    )
    