from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table, Enum
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Index, DateTime
from user.models import BaseObject

class Prompt(BaseObject):
    __tablename__ = "prompt"

    name = Column(String(100), index=True)
    description = Column(Text)
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    variables = Column(Text, nullable=True)
    realm_id = Column(String(36), ForeignKey("realm.id"))
    tags = relationship("Tag", secondary="prompt_tag", back_populates="prompts")


class Tag(BaseObject):
    __tablename__ = "tag"
    category = Column(String(50))
    name = Column(String(100))
    realm_id = Column(String(36), ForeignKey("realm.id"))
    prompts = relationship("Prompt", secondary="prompt_tag", back_populates="tags")


class PromptTag(Base):
    __tablename__ = 'prompt_tag'
    
    # Ensure these match exactly with the referenced columns
    prompt_id = Column(String(36), ForeignKey('prompt.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(String(36), ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)

    created_by = Column(String(256), index=True)
    updated_by = Column(String(256), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Add explicit indexes for better performance
    __table_args__ = (
        Index('idx_prompt_tag_prompt_id', 'prompt_id'),
        Index('idx_prompt_tag_tag_id', 'tag_id')
    )