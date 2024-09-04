#!/usr/bin/env python3
from openai import OpenAI
from dotenv import load_dotenv
import os, sys
import argparse
from loguru import logger


load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

class LlmAgent:

    def __init__(self, **kwargs):
        api_key = kwargs.get("api_key", os.getenv("DS_LLM_API_KEY"))
        base_url = kwargs.get("base_url", os.getenv("DS_LLM_BASE_URL"))
        model = kwargs.get("model", "deepseek-coder")

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def send_messages(self, messages, tools):
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools
        )
        return response.choices[0].message

    def ask_question(self, question: str):

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {'role': 'user', 'content': question}
            ],
            stream=True
        )

        for chunk in response:
            if "None" == chunk:
                continue
            print(chunk.choices[0].delta.content, end='')
        print("")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--action','-a', action='store', dest='action', help='specify action: ask|test')
    parser.add_argument('--model', '-m', dest='model', default="alibaba/Qwen1.5-110B-Chat", help='LLM model')
    parser.add_argument('--question', '-q', dest='question', default="什么是 RAG? 如何做 RAG?", help='you question')

    args = parser.parse_args()
    if (args.action == "test"):
        agent = LlmAgent(os.getenv("SF_LLM_API_KEY"), os.getenv("SF_LLM_BASE_URL"), args.model)
        agent.ask_question(args.question)
    else:
        print("example:")
        print("\t./ask_llm.py -a test")
