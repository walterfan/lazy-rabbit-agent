"""Unit tests for translation service: normalize input, truncation, output modes."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.translation.service import (
    _truncate_source,
    normalize_input_from_file,
    NormalizedInput,
)
from app.core.config import settings


class TestTruncateSource:
    """Test configurable max source length truncation."""

    def test_under_limit_unchanged(self):
        text = "Hello world."
        out, truncated = _truncate_source(text)
        assert out == text
        assert truncated is False

    def test_over_limit_truncated(self):
        max_len = getattr(settings, "TRANSLATION_MAX_SOURCE_LENGTH", 12_000)
        text = "x" * (max_len + 100)
        out, truncated = _truncate_source(text)
        assert len(out) <= max_len + 200  # suffix added
        assert truncated is True
        assert "截断" in out or "truncat" in out.lower() or "内容已截断" in out


class TestNormalizeInputFromFile:
    """Test file input normalization (text/plain, text/markdown)."""

    @pytest.mark.asyncio
    async def test_text_plain_utf8(self):
        content = "Hello, this is plain text."
        raw = content.encode("utf-8")
        result = await normalize_input_from_file(
            file_bytes=raw,
            content_type="text/plain",
            filename="test.txt",
        )
        assert isinstance(result, NormalizedInput)
        assert result.source_text == content
        assert result.truncated is False

    @pytest.mark.asyncio
    async def test_text_markdown_utf8(self):
        content = "# Title\n\nParagraph."
        raw = content.encode("utf-8")
        result = await normalize_input_from_file(
            file_bytes=raw,
            content_type="text/markdown",
            filename="doc.md",
        )
        assert result.source_text == content
        assert result.truncated is False

    @pytest.mark.asyncio
    async def test_unsupported_type_rejected(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            await normalize_input_from_file(
                file_bytes=b"binary",
                content_type="application/octet-stream",
                filename="x.bin",
            )

    @pytest.mark.asyncio
    async def test_empty_text_rejected(self):
        with pytest.raises(ValueError, match="no extractable text"):
            await normalize_input_from_file(
                file_bytes=b"   \n\n   ",
                content_type="text/plain",
                filename="empty.txt",
            )
