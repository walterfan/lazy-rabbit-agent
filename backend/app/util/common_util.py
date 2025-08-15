
import os
import json
from datetime import datetime

import time
import json
from datetime import datetime
from loguru import logger
import webbrowser
from util.agent_logger import logger
from util.ws_util import WsMessage
import re

DEFAULT_REALM_ID="8a1af32c-5f7a-44a4-8292-f73cfcd84535"
DEFAULT_CUSTOMER_ID="00917908-33e0-4cb1-9b8d-64e420213f7b"

class LazyLlmError(Exception):
    def __init__(self, reason, original_exception):
        self.reason = reason
        self.original_exception = original_exception
        super().__init__(f"LLM Error: {original_exception}")

    def get_reason(self):
        return self.reason


def str2bool(arg):
    if not arg:
        return False
    if isinstance(arg, bool):
        return arg
    if arg.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    else:
        return False
    
def metrics_recorder(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"[metrics] {{\"name\": \"'{func.__name__}'\", \"duration\": {elapsed_time:.4f} }}")
        return result
    return wrapper

def diagnose_dict2list(diagnose_dict: dict[str, dict]) ->list[tuple[str, str, str]]:
    results = []
    for k, v in diagnose_dict.items():
        results.append((k, v["uuid"], v["category"]))
    return results

def measurements_dict2list(measurements_dict: dict[str, dict]):
    results = []
    for k, v in measurements_dict.items():
        results.append((k,  v["uuid"], v["desc"], v["defaultUnit"]))
    return results

def extract_numbers(text):
    numbers = re.findall(r'\d+\.\d+|\d+', text)
    return [float(num) for num in numbers]

def task_csv_to_json(csv_str: str) -> str:
    lines = csv_str.strip().split("\n")
    headers = lines[0].split(",")
    data = [dict(zip(headers, map(str.strip, line.split(",")))) for line in lines[1:]]
    return json.dumps(data, indent=2, ensure_ascii=False)

def extract_markdown_text(text):
    match = re.search(r"```markdown\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else None


def open_link(url):
    """
    Opens a URL in Google Chrome browser on macOS
    
    Args:
        url (str): The website URL to open (e.g., "https://www.example.com")
    """
    try:
        # Method 1: Using webbrowser with Chrome specified
        # This assumes Chrome is installed in the default Applications folder
        chrome_path = "open -a /Applications/Google\ Chrome.app %s"
        webbrowser.get(chrome_path).open(url)
        
    except webbrowser.Error:
        try:
            # Method 2: Fallback using os.system and 'open' command
            os.system(f"open -a 'Google Chrome' {url}")
        except Exception as e:
            print(f"Error opening URL: {e}")
            # Optional: Add tkinter messagebox to show error
            from tkinter import messagebox
            messagebox.showerror("Error", "Could not open URL in Chrome")


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

def get_default_realm_id():
    return DEFAULT_REALM_ID

def get_default_customer_id():
    return DEFAULT_CUSTOMER_ID