from __future__ import annotations
from typing import TYPE_CHECKING
from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import json
from datetime import datetime, timedelta
from util.agent_logger import logger
import util.ws_util as ws_util

import os
from database import get_db, engine
from user.auth import authenticate_user, create_access_token, verify_access_token
from agile.worker import Translator, Composer
from api.models import SearchPromptsRequest, SearchPromptsResponse
from service.llm_service import PromptTemplates
# Initialize the router
router = APIRouter()

# TTL cache: key is track_id, value is websocket message
g_msg_cache = TTLCache(maxsize=100, ttl=600)
g_ws_manager = ws_util.ConnectionManager()

debug_flag = os.getenv("DEBUG_FLAG", False)

# Route to get a token
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/prompts/search")
async def search_prompts(search_prompts_request: SearchPromptsRequest, prompt_templates=Depends(PromptTemplates), db: Session = Depends(get_db)):
    system_prompt_name = f"{search_prompts_request.command}_system_prompt"
    user_prompt_name = f"{search_prompts_request.command}_user_prompt"
    logger.debug(f"system_prompt_name: {system_prompt_name}, user_prompt_name: {user_prompt_name}")

    resp = SearchPromptsResponse(
        system_prompt = prompt_templates.get_prompt_tpl(system_prompt_name),
        user_prompt = prompt_templates.get_prompt_tpl(user_prompt_name))
    
    return resp

@router.get("/health")
async def health():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"time": current_time, "state": "up"}


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, token: str):

    if token == "202410032143":
        logger.debug(f"websocket {username} connected")
    else:
        logger.debug(f"websocket {username} with token {token} connected")
        verify_result = verify_access_token(token)
        if (not verify_result) :
            rs_dict = {"desc": "Invalid Token or Invitation code.", "code": 401}
            await g_ws_manager.connect(websocket, username)
            await g_ws_manager.send_message(json.dumps(rs_dict, indent=2, ensure_ascii=False), username)
            await g_ws_manager.disconnect(username)
            return

    await g_ws_manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            msg = ws_util.build_ws_message(username, data)
            logger.debug(f"received {data} -> {msg}")
            if msg.get_command() == "translate":
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                translator = Translator()
                await translator.execute({"text": msg.get_field_value("input")})
                rs_dict = {"time": current_time, "result": translator.get_result(), "code": 200}
                await g_ws_manager.send_message(json.dumps(rs_dict, indent=2, ensure_ascii=False), username)
            elif  msg.get_command() == "compose":
                composer = Composer()
                await composer.execute({"text": msg.get_field_value("input"), "language": "中文"})
                rs_dict = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": composer.get_result(),
                    "code": 200}
                await g_ws_manager.send_message(json.dumps(rs_dict, indent=2, ensure_ascii=False), username)
            elif  msg.get_command() == "summaize":
                active_users = g_ws_manager.get_active_connections()
                rs_dict = {"users": {', '.join(active_users)}, "code": 200}
                await g_ws_manager.send_message(json.dumps(rs_dict, indent=2, ensure_ascii=False), username)
            else:
                rs_dict = {"desc": "Invalid command. Use 'translate, summarize, analyze, mindmap'.", "code": 400}
                await g_ws_manager.send_message(json.dumps(rs_dict, indent=2, ensure_ascii=False), username)
    except WebSocketDisconnect:
        g_ws_manager.disconnect(username)
        