from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table, Enum
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, BigInteger, DateTime

class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    variables = Column(Text, nullable=True)

    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()))
    created_by = Column(String(50))
    updated_by = Column(String(50))

    tags = relationship("Tag", secondary="prompt_tag", back_populates="prompts")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50))
    name = Column(String(50))
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_by = Column(String(50))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    prompts = relationship("Prompt", secondary="prompt_tag", back_populates="tags")

class PromptTag(Base):
    __tablename__ = 'prompt_tag'
    prompt_id = Column(Integer, ForeignKey('prompt.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
