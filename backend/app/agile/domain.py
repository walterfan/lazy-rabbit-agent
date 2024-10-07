"""
model of agile method

* story
* feature
* initiative
* sprint
* bug
* backlog
* meeting
  - sprint plan
  - sprint review
  - sprint retrospective

"""
from pydantic import BaseModel, UUID4
from enum import Enum

"""
priority: P1(Must have) / P2(Should have) / P3(Could have) / P4(Won't have)
"""
class StoryPriority(Enum):
    MUST_HAVE = 1
    SHOULD_HAVE = 2
    COULD_HAVE = 3
    WONT_HAVE = 4
"""
story state: OPEN, TODO, DOING, TO_VERIFY, DONE, CLOSED
"""
class StoryState(Enum):
    OPEN = 0
    TODO = 1
    DOING = 2
    TO_VERIFY = 3
    DONE = 4
    CLOSED = 5

"""
title: As a Role, I want to Action, so that benefit
* Title
* Feature
* Priority
* Description
* A
* Verifier

"""
class Story(BaseModel):
    id: UUID4
    feature: UUID4
    priority: StoryPriority
    state: StoryState

    title: str
    desc: str
    acceptance_criteria: str
    author: str
    verifier: str