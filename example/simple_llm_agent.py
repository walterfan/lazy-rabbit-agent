#!/usr/bin/env python3
from typing import Type
from pydantic import BaseModel
from typing import Iterable
import instructor
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletionMessage
from dotenv import load_dotenv
import os, sys
import argparse
from loguru import logger


load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

def str2bool(arg):
    if isinstance(arg, bool):
        return arg
    if arg.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif arg.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class LlmAgent:

    def __init__(self, **kwargs):
        api_key = kwargs.get("api_key", os.getenv("LLM_API_KEY"))
        base_url = kwargs.get("base_url", os.getenv("LLM_BASE_URL"))
        model = kwargs.get("model", os.getenv("LLM_MODEL"))
        stream = kwargs.get("stream", False)
        logger.debug(f"base_url={base_url}, model={model} stream={stream}")
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._instructor = instructor.from_openai(self._client)

        self._model = model
        self._stream = stream

    def get_json_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={
                'type': 'json_object'
            },

            max_tokens = kwargs.get("max_token", 8192),
            temperature = kwargs.get("temperature", 0.5),
            stream = kwargs.get("stream", False),
        )
        return response.choices[0].message.content

    def get_objects_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> list:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        user_objects = self._instructor.chat.completions.create(
            model=self._model,
            messages=messages,
            response_model=Iterable[user_model],
            max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
            temperature = kwargs.get("LLM_TEMPERATURE", 0.5),
            stream = kwargs.get("stream", False),
        ) # type: ignore
        return user_objects

    def get_object_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> list:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        user_object = self._instructor.chat.completions.create(
            model=self._model,
            messages=messages,
            response_model=user_model,
            max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
            temperature = kwargs.get("LLM_TEMPERATURE", 0.5),
            stream = kwargs.get("stream", False),
        ) # type: ignore
        return user_object


    def send_messages(self, messages, tools) -> ChatCompletionMessage:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools
        )
        return response.choices[0].message

    def ask_question(self, question: str) -> str:

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {'role': 'user', 'content': question}
            ],
            stream=self._stream
        )
        answer = ""
        if self._stream:
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    answer += content
                    print(content, end="")
        else:
            answer = response.choices[0].message.content
        return answer

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--action','-a', action='store', dest='action', help='specify action: ask|test')
    parser.add_argument('--model', '-m', dest='model', default="Qwen/Qwen2-7B-Instruct", help='LLM model')
    parser.add_argument('--stream,', '-s', type=str2bool, dest='stream', default=True, help='LLM stream method')
    parser.add_argument('--question', '-q', dest='question', default="大语言模型应用中, 如何做 RAG? 请具体解释一下概念和方法, 并举出实例", help='you question')

    args = parser.parse_args()
    if (args.action == "test"):
        logger.info(f"User> {args.question}")
        agent = LlmAgent(api_key=os.getenv("SF_LLM_API_KEY"), base_url=os.getenv("SF_LLM_BASE_URL"),
                         model=args.model, stream=args.stream)
        answer = agent.ask_question(args.question)
        if not args.stream:
            logger.info(f"Model> {answer}")
    else:
        print("example:")
        print("\t./ask_llm.py -a test")
    logger.info("Goodbye :)")