#!/usr/bin/env python3
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import os, sys
from dotenv import load_dotenv

load_dotenv()


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]




model = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.getenv("LLM_API_KEY"),
    openai_api_base=os.getenv("LLM_BASE_URL"),
    max_tokens=4096
)

with_message_history = RunnableWithMessageHistory(model, get_session_history)

system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

parser = StrOutputParser()

config = {"configurable": {"session_id": "waltertest"}}

response = with_message_history.invoke(
    [HumanMessage(content="Hi! I'm Bob")],
    config=config,
)
response = with_message_history.invoke(
    [HumanMessage(content="What's my name?")],
    config=config,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | model

result = chain.invoke({"language": "chinese", "text": "As you sow, so shall you reap"})
print(result)