"""Translation agent service: URL/file → source text → LLM translate + explain + summarize."""

from app.services.translation.service import (
    TranslationResult,
    TranslationService,
    normalize_input_from_file,
    normalize_input_from_text,
    normalize_input_from_url,
)

__all__ = [
    "TranslationResult",
    "TranslationService",
    "normalize_input_from_file",
    "normalize_input_from_text",
    "normalize_input_from_url",
]
