#!/usr/bin/env python3
import os, sys
import json
from typing import Type
from pydantic import BaseModel
from jinja2 import Template
# for testing
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import asyncio
from backend.app.service.async_llm_client import AsyncLlmClient, str2bool
from yaml_config import YamlConfig

from loguru import logger

def list2str(l: list[str]) -> str:
    rs = ""
    for item in l:
        if len(rs) > 0:
            rs += ", "
        rs += f"'{item}'"
    return rs

def read_llm_config(config: YamlConfig):
    base_url = config.get_config_item_2("llm", "base_url") or os.getenv("LLM_BASE_URL")
    api_key = config.get_config_item_2("llm", "api_key") or os.getenv("LLM_API_KEY")
    model = config.get_config_item_2("llm", "model") or os.getenv("LLM_MODEL")
    stream = config.get_config_item_2("llm", "stream") or os.getenv("LLM_STREAM")
    return LlmConfig(base_url=base_url, api_key=api_key, model=model, stream=stream)


class PromptTemplates:

    def __init__(self, config_file):
        self._yaml_config = YamlConfig(config_file)
        self._prompt_config = self._yaml_config.get_config_data()

    def get_prompt_tpl(self, cmd):
        return self._prompt_config.get(cmd)

    def get_prompts(self):
        return self._prompt_config.keys()

class LlmConfig:
    base_url: str
    api_key: str
    model: str
    stream: bool

    def __init__(self, **kwargs):
        self.base_url = kwargs.get("base_url", os.getenv("LLM_BASE_URL"))
        self.api_key = kwargs.get("api_key", os.getenv("LLM_API_KEY"))
        self.model = kwargs.get("model", os.getenv("LLM_MODEL"))
        self.stream = str2bool(kwargs.get("stream", os.getenv("LLM_STREAM")))

    def __repr__(self) -> str:
        return f"LlmConfig(base_url={self.base_url}, api_key={self.api_key}, model={self.model}, stream={self.stream})"

    def __hash__(self):
        return hash((self.base_url, self.api_key, self.model, self.stream))

    def __eq__(self, other):
        if isinstance(other, LlmConfig):
            return (self.base_url, self.api_key, self.model, self.stream) == (other.base_url, other.api_key, other.model, other.stream)
        return False

class LlmService:
    def __init__(self, llm_config: LlmConfig, prompt_config_file: str = f"{CURRENT_DIR}/prompt_template.yaml"):
        self._llm_client = AsyncLlmClient(base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            model=llm_config.model,
            stream=llm_config.stream)
        if prompt_config_file:
            self._prompt_templates = PromptTemplates(prompt_config_file)

    def get_llm_client(self):
        return self._llm_client

    def get_prompt_templates(self):
        return self._prompt_templates

    def get_prompt_template(self, prompt_name):
        return self._prompt_templates.get_prompt_tpl(prompt_name)

    def get_default_system_prompt(self):
        return self._prompt_templates.get_prompt_tpl("system_prompt")

    def build_user_prompt(self, data_dict: dict, prompt_name='user_prompt') -> str:
        user_prompt_tpl = self._prompt_templates.get_prompt_tpl(prompt_name)
        template = Template(user_prompt_tpl)
        rendered_str = template.render(data_dict)
        return rendered_str

    def build_prompt(self, data_dict: dict, user_prompt_tpl: str) -> str:
        template = Template(user_prompt_tpl)
        rendered_str = template.render(data_dict)
        return rendered_str

    async def ask(self, system_prompt, user_prompt) -> str:
        logger.debug(f"Ask LLM for str: {system_prompt}, {user_prompt}.")
        return await self._llm_client.get_llm_response(system_prompt, user_prompt)

    async def ask_as_json_str(self, system_prompt, user_prompt) -> str:
        logger.debug(f"Ask LLM for json: {system_prompt}, {user_prompt}.")
        return await self._llm_client.get_json_response(system_prompt, user_prompt)

    async def ask_as_resp_models(self, system_prompt, user_prompt, user_model: Type[BaseModel]) -> list[BaseModel]:
        logger.debug(f"Ask LLM for resp models: {system_prompt}, {user_prompt}.")
        return await self._llm_client.get_objects_response(system_prompt, user_prompt, user_model) # type: ignore

    async def ask_as_resp_model(self, system_prompt, user_prompt, user_model: Type[BaseModel]) -> BaseModel:
        logger.debug(f"Ask LLM for resp model: {system_prompt}, {user_prompt}.")
        return await self._llm_client.get_object_response(system_prompt, user_prompt, user_model) # type: ignore

    def parse_llm_response(self, response: str) -> dict:
        response_json = json.loads(response)
        return response_json

    async def ask_as_resp_stream(self, system_prompt, user_prompt, is_print=False):
        if is_print:
            async for chunk in self._llm_client.get_response_stream(system_prompt, user_prompt):
                print(chunk, end="", flush=True)  # Print each chunk as it arrives
        else:
            return self._llm_client.get_response_stream(system_prompt, user_prompt)

g_llm_service = None

def get_llm_service_instance(llm_config: LlmConfig, prompt_config_file: str = None) -> LlmService:
    global g_llm_service
    if g_llm_service is None:
        g_llm_service = LlmService(llm_config, prompt_config_file)
    return g_llm_service

if __name__ == "__main__":
    import dotenv
    import argparse

    # Load environment variables
    dotenv.load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process system and user prompts.")
    parser.add_argument("-s", "--system_message", type=str, help="System message for LLM")
    parser.add_argument("-u", "--user_message", type=str, help="User message for LLM")
    parser.add_argument("-t", "--template", type=str, help="prompt template name")
    args = parser.parse_args()

    config = YamlConfig("../etc/sticky_note.yaml")
    llm_config = read_llm_config(config)
    llm_config.stream = True
    logger.info(f"llm_config={llm_config}")

    if llm_config.api_key:
        llm_service = get_llm_service_instance(llm_config, "../etc/prompt_template.yaml")
        prompt_tpl = llm_service.get_prompt_template(args.template)
        if prompt_tpl is None:
            logger.error(f"prompt_tpl {prompt_tpl} is not found")
            sys.exit(1)
        print(prompt_tpl)
        asyncio.run(llm_service.ask_as_resp_stream(prompt_tpl.get("system_prompt"), prompt_tpl.get("user_prompt"), True))