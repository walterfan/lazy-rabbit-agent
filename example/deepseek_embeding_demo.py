import httpx
import json
import os
from loguru import logger
import sys
from dotenv import load_dotenv

load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

api_url = os.getenv("LLM_BASE_URL1")
api_key = os.getenv("LLM_API_KEY1")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "text": "DeepSeek is a powerful AI platform with Embedding support."
}

http_client = httpx.Client(verify=False)
response = http_client.post(api_url + "/v1/embedding", headers=headers, data=json.dumps(data))

if response.status_code == 200:
    embedding = response.json().get("embedding")
    logger.info("Generated Embedding: {}", embedding)
else:
    logger.error("Request failed: {} {}", response.status_code, response.text)