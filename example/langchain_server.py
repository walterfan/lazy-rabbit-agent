from typing import List
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain.chat_models import ChatOpenAI
from langserve import add_routes

import os, sys
import argparse
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
    max_tokens=1024
)


class CommaSeparatedListOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        return text.strip().split(", ")

system_template = """你是一个能生成以逗号分隔列表的助手, 用户会传入一个类别, 你会生成该类别下的5种对象,
并以逗号分隔的型号返回, 不要包含其他内容."""

human_template = "{text}"

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("human", human_template)
     ]
)

first_chain = chat_prompt | llm | CommaSeparatedListOutputParser()

app = FastAPI(
    title = "Langchain demo",
    version = "0.0.1",
    description = "langchain application interface"
)

add_routes(app, first_chain, path="/demo")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=2024)