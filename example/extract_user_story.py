from pydantic import BaseModel
from typing import Type, Enum
from datetime import datetime, timedelta
import asyncio
from async_llm_agent import AsyncLlmAgent
class User(BaseModel):
    username: str
    fullname: str
    email: str

class IssuePriority(Enum):
    """
    priority: P1(Must have) / P2(Should have) / P3(Could have) / P4(Won't have)
    """
    MUST_HAVE = 1
    SHOULD_HAVE = 2
    COULD_HAVE = 3
    WONT_HAVE = 4

class IssueState(Enum):
    """
    story state: OPEN, TODO, DOING, TO_VERIFY, DONE, CLOSED
    """
    OPEN = 0
    TODO = 1
    DOING = 2
    TO_VERIFY = 3
    DONE = 4
    CLOSED = 5

class UserStory(BaseModel):
    """
    user story need acceptance_criteria(DoD: Definition of Done)
    """
    sn : int
    title: str
    priority: IssuePriority
    state: IssueState
    author: User
    assignee: User
    title: str
    description: str
    labels: list[str]
    deadline: datetime
    estimation: timedelta
    acceptance_criteria: str
    verifier: User

def demo():
    pass


if __name__ == "__main__":
    demo()