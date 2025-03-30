from pydantic import BaseModel
from datetime import datetime, timedelta
import json
class UserBase(BaseModel):
    username: str
    email: str
    status: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

#-------- Define the Task schema ----------
# Define the TaskCreate schema
class TaskCreate(BaseModel):
    title: str
    description: str
    priority: int
    duration: int

class TaskResult(BaseModel):
    track_id: str
    task_status: int
    task_content: str


class Task(BaseModel):
    """
    表示一个任务的模型。

    属性:
        id (int): 任务的唯一标识符。
        title (str): 任务的标题。
        description (str): 任务的详细描述。
        priority (int): 任务的优先级。priority 表示任务的优先级
            1: Must have
            2: Should have
            3: Could have
            4: Won't have
        workload (str): 任务的工作量, 以 T-shirt Size 来标识
            S: Small = less that 1 hour
            M: Medium = 2 hours
            L: Large = 4 hours
            XL: Extra Large = more than 6 hours
        deadline (datetime): 任务的截止日期
        difficulty (int): 任务的难度级别。
            1: time-consuming and energy-consuming
            2: energy-consuming
            3: time-consuming
            4: easy to do
    """
    id: int
    title: str
    description: str
    priority: int
    duration: timedelta
    deadline: datetime
    difficulty: int

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "priority": self.priority,
            "duration": self.duration.total_seconds()/60,
            "deadline": self.deadline.isoformat(),

        }
    def to_json(self):
        return json.dumps(self.to_dict())

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models



class TaskBuilder:
    def __init__(self):
        self.title = None
        self.description = None
        self.priority = None
        self.duration = None
        self.deadline = None
        self.difficulty = None

    def title(self, title: str):
        self.title = title
        return self

    def description(self, description: str):
        self.description = description
        return self

    def priority(self, priority: int):
        self.priority = priority
        return self

    def duration(self, duration: timedelta):
        self.duration = duration
        return self

    def deadline(self, deadline: datetime):
        self.deadline = deadline
        return self

    def difficulty(self, difficulty: int):
        self.difficulty = difficulty
        return self

    def build(self) -> Task:
        if not all([self.title, self.priority, self.duration, self.deadline, self.difficulty]):
            raise ValueError("All fields must be set before building the Task object.")
        return Task(
            id=0,  # Assuming id is auto-generated, you might want to handle this differently
            title=self.title,
            description=self.description,
            priority=self.priority,
            duration=self.duration,
            deadline=self.deadline,
            difficulty=self.difficulty
        )

today_tasks = """
title, priority, difficulty, duration, deadline
update design, 1, 2, 120, 2025-02-17
coding for backend service, 1, 2, 120, 2025-02-17
learn channel of go, 3, 2, 120, 2025-02-17
coding of shell script, 1, 2, 120, 2025-02-17
write my blog, 3, 2, 60, 2025-02-23
write my book, 3, 2, 60, 2025-02-23
learn english, 2, 2, 30, 2025-02-17
Physical exercise, 2, 2, 60, 2025-02-17
check email and IM, 1, 2, 30, 2025-02-17
learn domain knowledge, 2, 2, 120, 2025-02-24
"""

def task_csv_to_json(csv_str: str) -> str:
    lines = csv_str.strip().split("\n")
    headers = lines[0].split(",")
    data = [dict(zip(headers, map(str.strip, line.split(",")))) for line in lines[1:]]
    return json.dumps(data)