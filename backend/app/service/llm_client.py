#!/usr/bin/env python3
import os
import sys

from typing import Type, List, Union
from pydantic import BaseModel

from typing import Iterable, Literal
import instructor
from openai import OpenAI
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying, stop_after_attempt, wait_fixed, retry_if_not_exception_type

# for testing
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from util.agent_logger import logger

def str2bool(arg):
    if not arg:
        return False
    if isinstance(arg, bool):
        return arg
    if arg.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    else:
        return False

class LlmClient:

    def __init__(self, **kwargs):
        self._api_key = kwargs.get("api_key", os.getenv("LLM_API_KEY"))
        self._base_url= kwargs.get("base_url", os.getenv("LLM_BASE_URL"))
        self._model = kwargs.get("model", os.getenv("LLM_MODEL"))
        self._stream = str2bool(kwargs.get("stream", os.getenv("LLM_STREAM")))
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        self._instructor = instructor.from_openai(self._client, mode=instructor.Mode.TOOLS)

    def get_str_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens = kwargs.get("max_token", 4096),
            temperature = kwargs.get("temperature", 0.5),
            stream = kwargs.get("stream", False),
        )
        return response.choices[0].message.content

    def get_json_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={ 'type': 'json_object' },
            max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
            temperature = kwargs.get("LLM_TEMPERATURE", 0.5),
            stream = kwargs.get("stream", False),
        ) # type: ignore
        #logger.debug(f"---debug---{messages}, {response}")
        return response.choices[0].message.content


    def get_objects_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> list:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        try:
            user_objects = self._instructor.chat.completions.create(
                model=self._model,
                messages=messages,
                response_model=Iterable[user_model],
                max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
                temperature = kwargs.get("LLM_TEMPERATURE", 0.5),
                stream = kwargs.get("stream", False),
                max_retries=Retrying(
                    stop=stop_after_attempt(2),
                    wait=wait_fixed(1),
                ) # type: ignore
            ) # type: ignore
            return user_objects
        except InstructorRetryException as e:
            logger.error(f"attempt={e.n_attempts},last_completion={e.last_completion}, messages={e.messages}")
            return []
        except Exception as e:
            # If an error occurs, log it
            logger.error(f"An error occurred: {e}")

            # Optionally, log any partial response you can access (if it's available before validation)
            if hasattr(e, 'response'):  # Check if the exception has a 'response' attribute
                logger.error(f"LLM Partial Response: {e.response}")

            raise # Re-raise the exception if needed

    # refer to https://python.useinstructor.com/concepts/retrying/#simple-max-retries
    def get_object_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> dict:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        try:
            user_object = self._instructor.chat.completions.create(
                model=self._model,
                messages=messages,
                response_model=user_model,
                max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
                temperature = kwargs.get("LLM_TEMPERATURE", 0.5),
                stream = kwargs.get("stream", False),
                max_retries=Retrying(
                    stop=stop_after_attempt(2),
                    wait=wait_fixed(1),
                )# type: ignore
            ) # type: ignore
        except InstructorRetryException as e:
            logger.error(e.messages[-1]["content"])  # type: ignore
            logger.error(f"attempt={e.n_attempts},last_completion={e.last_completion}, messages={e.messages}")
            return {}
        return user_object
