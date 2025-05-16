import asyncio
import os
import time
import json
import httpx
from celery import current_task
from concurrent import futures
from util.agent_logger import logger
from worker.celery_app import celery_app

from cachetools import TTLCache

BASE_URL = os.getenv("LLM_AGENT_URL")
USERNAME = os.getenv("LLM_AGENT_USERNAME")
PASSWORD = os.getenv("LLM_AGENT_PASSWORD")

# refer to https://cachetools.readthedocs.io/en/latest/#cachetools.TTLCache
# token keep in memory for 50*60 = 3000 seconds -> 50 minutes because token is valid for 1 hour
g_token_cache = TTLCache(maxsize=100, ttl=3000)

@celery_app.task
def long_task(word: str) -> dict:
    logger.info("long_task called")
    asyncio.run(long_async_task())
    return {'result': word}

async def long_async_task():
    for i in range(10):
        await asyncio.sleep(1)

@celery_app.task
def plan_task(msg: str) -> dict:
    logger.info("text_analysis_task called for {msg}")
    #asyncio.run(do_plan(msg))
    return {'code': 0, 'desc': 'ok'}

@celery_app.task
def exec_task(msg: str) -> dict:
    logger.info("report_analysis_task called for {msg}")
    #asyncio.run(do_exec(msg))
    return {'code': 0, 'desc': 'ok'}