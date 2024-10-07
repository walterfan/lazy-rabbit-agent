#!/usr/bin/env python3
from pydantic import BaseModel
from fastapi import FastAPI
from openai import AsyncOpenAI
import logfire
from async_llm_agent import AsyncLlmAgent
import asyncio
from collections.abc import Iterable
from fastapi.responses import StreamingResponse

# request
class UserData(BaseModel):
    query: str


# response
class UserDetail(BaseModel):
    name: str
    age: int

class MultipleUserData(BaseModel):
    queries: list[str]

app = FastAPI()
agent = AsyncLlmAgent()
#logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
logfire.configure(service_name='lazy-llm-agent')
logfire.instrument_pydantic()
logfire.instrument_openai(agent.get_llm_client(), suppress_other_instrumentation=True)
logfire.instrument_fastapi(app)

@app.post("/user", response_model=UserDetail)
async def endpoint_function(data: UserData) -> UserDetail:
    system_prompt = "You are a smart AI assitant"
    user_prompt = f"Extract: `{data.query}`"
    user_detail = await agent.get_object_response(system_prompt, user_prompt, UserDetail)

    return user_detail

@app.post("/many-users", response_model=list[UserDetail])
async def extract_many_users(data: MultipleUserData):
    async def extract_user(query: str):
        system_prompt = "You are a smart AI assitant"
        user_prompt = f"Extract: `{data.query}`"
        user_detail = await agent.get_object_response(system_prompt, user_prompt, UserDetail)

        logfire.info("/User returning", value=user_detail)
        return user_detail

    coros = [extract_user(query) for query in data.queries]
    return await asyncio.gather(*coros)

@app.post("/extract", response_class=StreamingResponse)
async def extract(data: UserData):
    system_prompt = "You are a smart AI assitant"
    user_prompt = f"Extract: `{data.query}`"
    users = await agent.get_objects_response(system_prompt, user_prompt, UserDetail, stream=True)

    async def generate():
        with logfire.span("Generating User Response Objects"):
            async for user in users:
                resp_json = user.model_dump_json()
                logfire.info("Returning user object", value=resp_json)

                yield resp_json

    return StreamingResponse(generate(), media_type="text/event-stream")


def act_as_client(port: int):
    import requests

    response = requests.post(
        f"http://127.0.0.1:{port}/extract",
        json={
            "query": "Alice and Bob are best friends. \
                They are currently 32 and 43 respectively. "
        },
        stream=True,
    )

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(str(chunk, encoding="utf-8"), end="\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--role','-r', action='store', dest='role', help='specify role: client|server')
    parser.add_argument('--port','-p', type=int, action='store', dest='port', default=2024, help='specify listen port')

    args = parser.parse_args()

    if (args.role=="client"):
        act_as_client(args.port)
    else:
        import uvicorn
        uvicorn.run(app, host="localhost", port=args.port)