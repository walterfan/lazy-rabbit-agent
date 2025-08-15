#!/usr/bin/env python3
import os
import logfire
import httpx
from pydantic import BaseModel
from openai import AsyncOpenAI
from typing import Iterable, Literal
import instructor
from instructor.exceptions import InstructorRetryException
from typing import Type, List, Union, AsyncGenerator
from loguru import logger
from common_util import LazyLlmError, str2bool

class AsyncLlmClient:

    def __init__(self, **kwargs):
        self._api_key = kwargs.get("api_key", os.getenv("LLM_API_KEY"))
        self._base_url= kwargs.get("base_url", os.getenv("LLM_BASE_URL"))
        self._model = kwargs.get("model", os.getenv("LLM_MODEL"))
        self._stream = str2bool(kwargs.get("stream", os.getenv("LLM_STREAM")))
        self._http_client = httpx.AsyncClient(verify=False)
        self._client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url, http_client=self._http_client)
        self._instructor = instructor.from_openai(self._client, mode=instructor.Mode.TOOLS)
        self._max_retry_count = 2
        if kwargs.get("service_name") is not None:
            logfire.configure(service_name=kwargs.get("service_name"))
            logfire.instrument_pydantic()
            logfire.instrument_openai(self._client, suppress_other_instrumentation=True)

    def get_openai_client(self):
        return self._client

    async def get_llm_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        logger.debug(f"{self._base_url}, {self._model}, {self._stream}: {messages}")
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream = kwargs.get("stream", False),
        ) # type: ignore
        return response.choices[0].message.content

    async def get_response_stream(self, system_prompt: str, user_prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Streams responses from the LLM in real-time.

        Args:
            system_prompt (str): The system prompt.
            user_prompt (str): The user prompt.
            **kwargs: Additional arguments for customization (e.g., model-specific parameters).

        Returns:
            AsyncGenerator[str, None]: A stream of content chunks from the LLM response.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        logger.debug(f"{self._base_url}, {self._model}, stream=True: {messages}")

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                stream=True,  # Enable streaming
                **kwargs
            )
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise

    async def get_json_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={
                'type': 'json_object'
            },
            max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
            temperature = kwargs.get("LLM_TEMPERATURE", 1.0),
            stream = kwargs.get("stream", False),
            max_retries = self._max_retry_count
        ) # type: ignore
        return response.choices[0].message.content

    async def get_objects_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> list:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        try:
            user_objects = await self._instructor.chat.completions.create(
                model=self._model,
                messages=messages,
                response_model=Iterable[user_model],
                max_tokens = kwargs.get("LLM_MAX_TOKEN", os.getenv("LLM_MAX_TOKEN", 4096)),
                temperature = kwargs.get("LLM_TEMPERATURE", os.getenv("LLM_TEMPERATURE", 1.0)),
                stream = kwargs.get("stream", False),
                max_retries = self._max_retry_count
            ) # type: ignore
            return user_objects
        except InstructorRetryException as e:
            reason = e.messages[-1]["content"] # type: ignore
            logger.error(f"attempt={e.n_attempts}, last_completion={e.last_completion}, {reason}")
            raise LazyLlmError(reason, e)
        except Exception as e:
            # If an error occurs, log it
            logger.error(f"An error occurred: {e}")

            # Optionally, log any partial response you can access (if it's available before validation)
            if hasattr(e, 'response'):  # Check if the exception has a 'response' attribute
                logger.error(f"LLM Partial Response: {e.response}") # type: ignore
                raise LazyLlmError(e.response, e) # type: ignore

            raise LazyLlmError(f"An error occurred: {e}", e) # type: ignore


    # refer to https://python.useinstructor.com/concepts/retrying/#simple-max-retries
    async def get_object_response(self, system_prompt: str, user_prompt: str, user_model: Type[BaseModel], **kwargs) -> dict:
        messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        try:
            user_object = await self._instructor.chat.completions.create(
                model=self._model,
                messages=messages,
                response_model=user_model,
                max_tokens = kwargs.get("LLM_MAX_TOKEN", 4096),
                temperature = kwargs.get("LLM_TEMPERATURE", 1.0),
                stream = kwargs.get("stream", False),
                max_retries = self._max_retry_count
            ) # type: ignore
        except InstructorRetryException as e:
            reason = e.messages[-1]["content"] # type: ignore
            logger.error(f"attempt={e.n_attempts}, last_completion={e.last_completion}, {reason}")
            raise LazyLlmError(reason, e)
        return user_object
