#!/usr/bin/env python3
import requests
import os
import json
class SiliconflowClient:
    def __init__(self, base_url, api_key) -> None:
        self._base_url = base_url
        self._api_key = api_key
    def get_model_info(self) -> dict:
        url = f"{self._base_url}/models"

        headers = {"Authorization": f"Bearer {self._api_key}"}

        response = requests.request("GET", url, headers=headers)

        return json.loads(response.text)

    def get_user_info(self) -> dict:
        url = f"{self._base_url}/user/info"

        headers = {"Authorization": f"Bearer {self._api_key}"}

        response = requests.request("GET", url, headers=headers)

        return json.loads(response.text)

    def ask(self, question):

        url = f"{self._base_url}/chat/completions"

        payload = {
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "stream": False,
            "max_tokens": 512,
            "stop": ["quit"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "json_object"}
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return json.loads(response.text)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--action','-a', action='store', dest='action', help='specify action: ask|chat|query')
    parser.add_argument('--key', '-p', dest='api_key', help='LLM api key')
    parser.add_argument('--url', '-u', dest='base_url', help='LLM base url')
    parser.add_argument('--question', '-q', dest='question', help='question')
    parser.add_argument('--case', '-c', dest='case', default="default", help='specify test case')

    args = parser.parse_args()
    import dotenv
    dotenv.load_dotenv()
    base_url = os.getenv("SILICONFLOW_BASE_URL")
    api_key = os.getenv("SILICONFLOW_API_KEY")
    print(f"base_url={base_url}, api_key={api_key}")
    client = SiliconflowClient(base_url, api_key)

    if (args.action=="query"):
        model_info =client.get_model_info()
        print(json.dumps(model_info, indent=2, ensure_ascii=False))

        user_info = client.get_user_info()
        print(json.dumps(user_info, indent=2, ensure_ascii=False))
    elif (args.action=="ask" and args.question):
        answer = client.ask(args.question)
        print(json.dumps(answer, indent=2, ensure_ascii=False))

    else:
        print("Not implemented")