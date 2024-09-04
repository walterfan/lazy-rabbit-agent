from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser

import pprint
import os, sys
import json
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
logger.add(sys.stdout,
           format="{time} {message}",
           filter="client",
           level="DEBUG")

llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("DS_LLM_API_KEY"),
    openai_api_base=os.getenv("DS_LLM_BASE_URL"),
    max_tokens=4096
)


class JsonOutputParser(BaseOutputParser[dict]):
    def parse(self, text: str) -> List[str]:
        text = text.lstrip("```json").rstrip("```")
        return json.loads(text)


system_template = """你是一个能解释医生说话内容的助手, 当医生输入一段话, 你会解析其内容将它转换成 JSON 格式"""

human_template = """
将以下医生的描述转换成JSON格式：

描述: "{text}"

JSON格式:
{{
    "patient_name": "",
    "age": "",
    "symptoms": [],
    "diagnosis": "",
    "treatment_plan": ""
}}
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("human", human_template)
     ]
)

if __name__ == "__main__":
    chain = chat_prompt | llm | JsonOutputParser()
    user_prompt = "患者名叫李雷，35岁，出现了发烧和咳嗽的症状。诊断为急性支气管炎，建议服用抗生素并多喝水。"
    result = chain.invoke({"text", user_prompt})
    pprint.pprint(result)