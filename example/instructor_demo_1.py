#!/usr/bin/env python3
import simple_llm_agent
from pydantic import BaseModel
from typing import Type
import asyncio

# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int


def demo():
    llm_agent = simple_llm_agent.LlmAgent()

    # Extract structured data from natural language
    user_info = llm_agent.get_object_response("You are a smart analyst", "John Doe is 30 years old.", UserInfo)

    print(user_info.name)
    #> John Doe
    print(user_info.age)


if __name__ == "__main__":
    demo()