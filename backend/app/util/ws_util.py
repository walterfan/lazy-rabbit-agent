from fastapi import WebSocket
import json
import sys
from util.agent_logger import logger
from typing import Deque, List
from datetime import datetime



class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    def get_auth_header(self, websocket: WebSocket):
        auth_header = websocket.headers.get("Authorization")

        if not auth_header:
            #await websocket.close(code=1008, reason="Authorization header missing")
            return ""

        try:
            # Extract Bearer token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            return token
        except ValueError:
            #await websocket.close(code=1008, reason="Invalid Authorization header format")
            return ""

    async def accept(self, websocket: WebSocket, name: str):
        await websocket.accept()
        self.active_connections[name] = websocket

    async def disconnect(self, name: str, code=1000, reason=""):
        if name in self.active_connections:
            websocket = self.active_connections.pop(name)
            await websocket.close(code, reason)
            #del self.active_connections[name]
    async def send_message(self, message: str, name: str):
        websocket = self.active_connections.get(name)
        if websocket:
            await websocket.send_text(message)
            #logger.debug(f"websocket {name} sent message {message}")
        else:
            logger.error(f"websocket {name} not found")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def get_active_connections(self):
        return list(self.active_connections.keys())

class WsMessage:
    """
    Class to hold the message received over web socket
    """
    def __init__(self, payload):
        self._payload = payload
        try:
            self._data = json.loads(payload)
        except:
            print(f"cannot parse payload {payload}")
            self._data = {}
        self._user = self.get_field_value("user", "")
        self._command = self.get_field_value("cmd", "")
        self._from = self.get_field_value("from", "")
        self._to = self.get_field_value("to", "")
        self._seq = self.get_field_value("seq", 0)
        self._time = self.get_field_value("time", 0)

    def get_command(self):
        return self._command

    def get_user(self):
        return self._user

    def set_user(self, user):
        self._user = user

    def get_data(self):
        return self._data

    def get_field_value(self, field_name, default_value=""):
        return self._data.get(field_name, default_value)

    def __repr__(self) -> str:
        return f"cmd={self._command}, user={self._user}, payload={self._payload}"

def build_ws_message(user: str, playload: str) -> WsMessage:
    ws_msg =  WsMessage(playload)
    ws_msg.set_user(user)
    return ws_msg

def handle_text_analysis(ws_msg: WsMessage) -> str:
    # post a task for LLM text analysis
    # reply ack first
    return create_text_analysis_ack(ws_msg)

def create_text_analysis_ack(ws_msg: WsMessage) -> str:
    json_dict = {}
    json_dict["cmd"] = ws_msg.get_command()
    json_dict["from"] = ws_msg.get_field_value("to")
    json_dict["to"] = ws_msg.get_field_value("from")
    json_dict["seq"] = ws_msg.get_field_value("seq")
    json_dict["time"] = int(datetime.now().timestamp() * 1000)
    json_dict["desc"] = "ok"
    json_dict["code"] = 101
    json_dict["track_id"] = ws_msg.get_field_value("track_id")
    return json.dumps(json_dict)