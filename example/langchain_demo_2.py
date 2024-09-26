#!/usr/bin/env python3
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import os, sys
from dotenv import load_dotenv

load_dotenv()


#os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
os.environ["USER_AGENT"] = "waltertest"
#os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()
#os.environ["OPENAI_API_KEY"] = getpass.getpass()

model = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("LLM_API_KEY"),
    openai_api_base=os.getenv("LLM_BASE_URL"),
    max_tokens=4096
)

system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

parser = StrOutputParser()

#result = model.invoke(messages)
#parser.invoke(result)
#result = prompt_template.invoke({"language": "Chinese", "text": "hi"})

chain = prompt_template | model | parser

result = chain.invoke({"language": "chinese", "text": "As you sow, so shall you reap"})
print(result)