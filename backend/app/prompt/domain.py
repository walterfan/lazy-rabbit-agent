from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta


class TagBase(BaseModel):
    id: Optional[int] = None
    category: str
    name: str

    class Config:
        orm_mode = True

class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str = Field(..., alias="systemPrompt")
    user_prompt: str = Field(..., alias="userPrompt")
    tags: Optional[List[TagBase]] = None
    variables: List[str] = None

    class Config:
        from_attributes = True  # This replaces orm_mode = True
        populate_by_name = True  # This replaces allow_population_by_field_name

class PromptCreate(PromptBase):
    created_by: str = Field(..., alias="createdBy")
    updated_by: str = Field(..., alias="updatedBy")

    class Config:
        from_attributes = True  # This replaces orm_mode = True
        populate_by_name = True  # This replaces allow_population_by_field_name

class PromptResponse(PromptBase):
    id: int
    created_at: int = Field(..., alias="createdAt")
    updated_at: int = Field(..., alias="updatedAt")
    created_by: str = Field(..., alias="createdBy")
    updated_by: str = Field(..., alias="updatedBy")

    class Config:
        from_attributes = True  # This replaces orm_mode = True
        populate_by_name = True  # This replaces allow_population_by_field_name

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = Field(None, alias="systemPrompt")
    user_prompt: Optional[str] = Field(None, alias="userPrompt")
    tags: Optional[List[TagBase]] = None
    updated_by: str = Field(..., alias="updatedBy")

    class Config:
        from_attributes = True  # This replaces orm_mode = True
        populate_by_name = True  # This replaces allow_population_by_field_name