
import os
import json
import httpx
import requests
from datetime import datetime
from util.agent_logger import logger
from util.ws_util import WsMessage

def build_text_analysis_response(orignal_msg: WsMessage, task_content: str) -> dict:
    json_dict = orignal_msg.get_data()
    if "asr_list" in json_dict:
        del json_dict["asr_list"]
    json_dict["code"] = 100
    json_dict["from"] = "cloud"
    json_dict["to"] = "report"
    json_dict["time"] = int(datetime.now().timestamp() * 1000)
    json_dict["analysis"] = [ json.loads(task_content) ]
    return json_dict

