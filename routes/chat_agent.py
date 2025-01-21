from fastapi import FastAPI, HTTPException, APIRouter, Path, Query, Body, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

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

router = APIRouter()

class AgentRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    message: str
    timestamp: str
    user: str
    chat_id: str

@router.post("/agent-response", response_model=AgentResponse)
async def generate_bot_response(request: AgentRequest,
                                session: dict = Depends(verify_token)
    ):
    
    chat_id = session["userId"]
    user = session["userName"]
    
    user_message = request.message
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

    if len(chat_history[chat_id]) > 50:
        chat_history[chat_id] = chat_history[chat_id][-50:]

    save_chat_history(chat_history)
        
    return AgentResponse(
        message=bot_response,
        timestamp=current_time,
        user=user,
        chat_id=chat_id
    )
    