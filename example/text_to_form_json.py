#!/usr/bin/env python3
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from async_llm_agent import AsyncLlmAgent
import asyncio
from pydantic import BaseModel, Field
from enum import Enum
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class Priority(Enum):
    HIGHEST = 1
    VERY_HIGH = 2
    HIGH = 3
    MEDIUM = 4
    LOW = 5

class Difficulty(Enum):
    EASIEST = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    HARDEST = 5

class TaskTag(BaseModel):
    """A tag for categorizing tasks"""
    name: str = Field(..., description="The name of the tag")

class Task(BaseModel):
    """
    Task model, all datetime fields are iso format with time zone
    """
    task_id: Optional[str] = Field(None, description="Unique identifier for the task")
    name: str = Field(..., description="The title or name of the task")
    desc: Optional[str] = Field(None, description="Detailed description of the task")
    priority: Priority = Field(..., description="Priority level, from 1 (highest) to 5 (lowest)")
    difficulty: Difficulty = Field(..., description="Difficulty level, from 1 (easiest) to 5 (hardest)")
    duration: Optional[float] = Field(None, description="Estimated time to complete the task in hours")
    remind_note: Optional[str] = Field(None, description="remind user with check points of the task")
    remind_time: Optional[datetime] = Field(None, description="When to remind the user about the task")
    schedule_time: Optional[datetime] = Field(None, description="When work on the task should begin")
    start_time: Optional[datetime] = Field(None, description="When work on the task began actually")
    end_time: Optional[datetime] = Field(None, description="When the task was completed")
    deadline: Optional[datetime] = Field(None, description="When the task is due")

    create_time: Optional[datetime] = Field(None, description="When the task is created, defaults to now")
    update_time: Optional[datetime] = Field(None, description="When the task is updated, defaults to now")

    tags: List[TaskTag] = Field(default_factory=list, description="List of tags associated with this task")

class TaskJSONGenerator:
    def __init__(self):
        """Initialize the TaskJSONGenerator with your OpenAI API key."""
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")

        self._agent = AsyncLlmAgent()

    async def extract_task_from_text(self, text: str) -> Task:
        """Extract task information from natural language text"""

        system_prompt="""
        You are an AI assistant specialized in extracting task information from text.
        You are also a smart task planner and manager.
        """
        user_prompt=f"""
        Extract as much relevant information as possible about the task being described as specified response format:
        ---
        {text}
        ---
        note: current time is {datetime.now().isoformat()}
        """

        return await self._agent.get_object_response(system_prompt, user_prompt, Task)

    async def generate_task_json(self, user_text: str) -> Dict[str, Any]:
        """
        Convert natural language text into a structured Task JSON.

        Args:
            user_text: A string containing the natural language description of the task

        Returns:
            A dictionary containing the structured task data
        """

        task_data = await self.extract_task_from_text(user_text)
        task_data.task_id = str(uuid.uuid4())
        task_data.create_time = datetime.now()
        task_data.update_time = datetime.now()

        return task_data.model_dump_json()



# Example usage:
if __name__ == "__main__":
    import json

    # Replace with your actual OpenAI API key
    generator = TaskJSONGenerator()

    # Example text
    text = """
    我下周二上午9点有一个重要的技术演示, 我需要提前一天花费2小时准备好相关的议程, 可运行的代码和PPT
    """
    task_json_str = asyncio.run(generator.generate_task_json(text))
    print(json.dumps(json.loads(task_json_str), indent=2, ensure_ascii=False))
