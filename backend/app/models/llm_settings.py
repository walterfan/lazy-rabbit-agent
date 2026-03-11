from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.base import Base


class LLMSettings(Base):
    """Per-user LLM configuration overrides.

    Each row stores one user's customized LLM provider settings.
    Fields left empty/null fall back to the server-wide env defaults.
    """

    __tablename__ = "llm_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)

    # Text generation
    chat_base_url = Column(String(500), nullable=True)
    chat_api_key = Column(Text, nullable=True)
    chat_model = Column(String(255), nullable=True)
    chat_temperature = Column(Float, nullable=True)

    # Embedding
    embedding_base_url = Column(String(500), nullable=True)
    embedding_api_key = Column(Text, nullable=True)
    embedding_model = Column(String(255), nullable=True)

    # Image generation
    image_base_url = Column(String(500), nullable=True)
    image_api_key = Column(Text, nullable=True)
    image_model = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
