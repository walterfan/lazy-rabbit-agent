from pydantic import BaseModel

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


# Define the TaskCreate schema
class TaskCreate(BaseModel):
    title: str
    description: str

#-------- Define the Task schema ----------
class Task(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models
    
class TaskResult(BaseModel):
    track_id: str
    task_status: int
    task_content: str

class Organ(BaseModel):
    name: str
    uuid: str

class Occupy(BaseModel):
    name: str
    uuid: str
    related_organ_uuid: str

class Measurement(BaseModel):
    name: str
    uuid: str
    value: float
    unit: str
    related_organ_uuid: str

class TextAnalysisResult(BaseModel):
    organs: list[Organ]
    occupies: list[Occupy]
    measurements: list[Measurement]
    diagnoses: list[str]

class TextAnalysisResponse(BaseModel):
    check_id: str
    picture_ids: list[str]
    analysis: dict[str, TextAnalysisResult]