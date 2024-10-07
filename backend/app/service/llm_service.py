#!/usr/bin/env python3
import os, sys
import json
from typing import Type
from pydantic import BaseModel
from jinja2 import Template
# for testing
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from service.llm_client import LlmClient, str2bool
from util.yaml_config import YamlConfig
from util.agent_logger import logger

def list2str(l: list[str]) -> str:
    rs = ""
    for item in l:
        if len(rs) > 0:
            rs += ", "
        rs += f"'{item}'"
    return rs

class PromptTemplates:

    def __init__(self, config_file = f"{CURRENT_DIR}/prompt_template.yml"):
        self._yaml_config = YamlConfig(config_file)
        self._prompt_config = self._yaml_config.get_config_data()

    def get_prompt_tpl(self, cmd):
        return self._prompt_config.get(cmd)

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

class LlmService:
    def __init__(self, llm_config: LlmConfig, prompt_config_file: str = f"{CURRENT_DIR}/prompt_template.yml"):
        self._llm_config = llm_config
        self._llm_client = LlmClient(base_url=llm_config.base_url, api_key=llm_config.api_key, model=llm_config.model)
        self._prompt_templates = PromptTemplates(prompt_config_file)

    def get_llm_config(self) -> LlmConfig:
        return self._llm_config

    def get_default_system_prompt(self):
        return self._prompt_templates.get_prompt_tpl("system_prompt")

    def get_system_prompt(self, prefix):
        return self._prompt_templates.get_prompt_tpl(f"{prefix}_system_prompt")

    def get_prompt(self, name):
        return self._prompt_templates.get_prompt_tpl(name)

    def build_user_prompt(self, data_dict: dict, prompt_name='user_prompt') -> str:
        user_prompt_tpl = self._prompt_templates.get_prompt_tpl(prompt_name)
        #logger.debug(f"{prompt_name}: {user_prompt_tpl}")
        template = Template(user_prompt_tpl)
        rendered_str = template.render(data_dict)
        return rendered_str

    def ask_as_str(self, system_prompt, user_prompt) -> str:
        logger.debug(f"Ask LLM for json: {system_prompt}, {user_prompt}.")
        return self._llm_client.get_str_response(system_prompt, user_prompt)

    def ask_as_json_str(self, system_prompt, user_prompt) -> str:
        logger.debug(f"Ask LLM for json: {system_prompt}, {user_prompt}.")
        return self._llm_client.get_json_response(system_prompt, user_prompt)

    def ask_as_resp_models(self, system_prompt, user_prompt, user_model: Type[BaseModel]) -> list[BaseModel]:
        logger.debug(f"Ask LLM for resp models: {system_prompt}, {user_prompt}.")
        return self._llm_client.get_objects_response(system_prompt, user_prompt, user_model) # type: ignore

    def ask_as_resp_model(self, system_prompt, user_prompt, user_model: Type[BaseModel]) -> BaseModel:
        logger.debug(f"Ask LLM for resp model: {system_prompt}, {user_prompt}.")
        return self._llm_client.get_object_response(system_prompt, user_prompt, user_model) # type: ignore

    def parse_llm_response(self, response: str) -> dict:
        response_json = json.loads(response)
        return response_json


g_llm_service = None

def get_llm_service_instance(llm_config: LlmConfig = LlmConfig()) -> LlmService:
    global g_llm_service
    if g_llm_service is None:
        g_llm_service = LlmService(llm_config)
    return g_llm_service

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--action','-a', action='store', dest='action', help='specify action: read|write|test')
    parser.add_argument('--key', '-p', dest='api_key', help='LLM api key')
    parser.add_argument('--url', '-u', dest='base_url', help='LLM url')
    parser.add_argument('--case', '-c', dest='case', default="default", help='specify test case')

    args = parser.parse_args()

    if (args.action=="test"):
        import dotenv
        dotenv.load_dotenv()

        if args.case == "default":
            data = {"text": "hello world"}
            llm_config = LlmConfig(
                base_url=os.getenv("DS_LLM_BASE_URL"),
                api_key=os.getenv("DS_LLM_API_KEY"),
                model=os.getenv("DS_LLM_MODEL"))
            print(llm_config)
            llm_service = get_llm_service_instance(llm_config)

            system_prompt = llm_service.get_system_prompt("translate")
            user_prompt = llm_service.build_user_prompt(data, "translate_user_prompt")


            logger.info(f"system_prompt: {system_prompt}")
            logger.info(f"user_prompt: {user_prompt}")

            llm_resp = llm_service.ask_as_json_str(system_prompt, user_prompt)
            logger.info(llm_resp)

        elif args.case == "extract":
            pass
            # extract diagnosis
            # extract occupying_lesion
    else:
        print("usage example: ./llm_service.py -a test")