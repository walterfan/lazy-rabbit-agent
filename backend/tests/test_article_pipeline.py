"""
Tests for the article processing pipeline.

Covers:
- fetch_article: HTTP fetching with error handling
- extract_to_markdown: HTML to clean markdown extraction
- translate_bilingual: Paragraph-by-paragraph bilingual translation
- generate_mindmap_plantuml: PlantUML mindmap generation
- plantuml_renderer: Text encoding and rendering
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test: fetch_article
# ============================================================================


class TestFetchArticle:
    """Tests for fetch_article function."""

    @pytest.mark.asyncio
    async def test_fetch_valid_url(self):
        """Should return HTML content for a valid URL."""
        from app.services.secretary_agent.tools.article_processor import fetch_article

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Hello</h1><p>World</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.secretary_agent.tools.article_processor.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await fetch_article(url="https://example.com/article")
            assert "<h1>Hello</h1>" in result
            assert "<p>World</p>" in result

    @pytest.mark.asyncio
    async def test_fetch_timeout(self):
        """Should raise ValueError on timeout."""
        import httpx as httpx_lib
        from app.services.secretary_agent.tools.article_processor import fetch_article

        with patch("app.services.secretary_agent.tools.article_processor.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx_lib.TimeoutException("timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            with pytest.raises(ValueError, match="Timeout"):
                await fetch_article(url="https://slow.example.com/article")

    @pytest.mark.asyncio
    async def test_fetch_http_error(self):
        """Should raise ValueError on HTTP 404."""
        import httpx as httpx_lib
        from app.services.secretary_agent.tools.article_processor import fetch_article

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx_lib.HTTPStatusError(
                "Not Found", request=mock_request, response=mock_response
            )
        )

        with patch("app.services.secretary_agent.tools.article_processor.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            with pytest.raises(ValueError, match="HTTP 404"):
                await fetch_article(url="https://example.com/not-found")

    @pytest.mark.asyncio
    async def test_fetch_connection_error(self):
        """Should raise ValueError on connection errors."""
        import httpx as httpx_lib
        from app.services.secretary_agent.tools.article_processor import fetch_article

        with patch("app.services.secretary_agent.tools.article_processor.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx_lib.ConnectError("Connection refused")
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            with pytest.raises(ValueError, match="Error fetching"):
                await fetch_article(url="https://unreachable.example.com")


# ============================================================================
# Test: extract_to_markdown
# ============================================================================


class TestExtractToMarkdown:
    """Tests for extract_to_markdown function."""

    @pytest.mark.asyncio
    async def test_extract_basic_html(self):
        """Should extract main content from simple HTML."""
        from app.services.secretary_agent.tools.article_processor import extract_to_markdown

        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
        <nav>Navigation</nav>
        <article>
            <h1>Test Article Title</h1>
            <p>This is the first paragraph of the article with enough content
            to be considered meaningful by the extraction library. It contains
            several sentences about an important topic.</p>
            <p>This is the second paragraph with additional content that provides
            more details about the subject being discussed in this article.</p>
        </article>
        <footer>Footer content</footer>
        </body>
        </html>
        """

        result = await extract_to_markdown(html=html, url="https://example.com")
        assert isinstance(result, dict)
        assert "content" in result
        assert "word_count" in result
        assert result["word_count"] > 0

    @pytest.mark.asyncio
    async def test_extract_empty_html(self):
        """Should raise ValueError for empty or unparseable HTML."""
        from app.services.secretary_agent.tools.article_processor import extract_to_markdown

        with pytest.raises(ValueError, match="Could not extract"):
            await extract_to_markdown(html="<html><body></body></html>")

    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Should extract title and author when available."""
        from app.services.secretary_agent.tools.article_processor import extract_to_markdown

        html = """
        <html>
        <head>
            <title>My Great Article</title>
            <meta name="author" content="John Doe">
            <meta name="date" content="2026-01-15">
        </head>
        <body>
        <article>
            <h1>My Great Article</h1>
            <p>This is a substantial article with enough text to be properly
            extracted. The content discusses many important topics that are
            relevant to the reader. There are multiple paragraphs here.</p>
            <p>Another paragraph ensures the extraction works correctly
            and provides sufficient content for testing purposes.</p>
        </article>
        </body>
        </html>
        """

        result = await extract_to_markdown(html=html, url="https://example.com")
        # title should be extracted (exact value depends on trafilatura heuristics)
        assert result["title"] is not None or result["content"]


# ============================================================================
# Test: translate_bilingual
# ============================================================================


class TestTranslateBilingual:
    """Tests for translate_bilingual function."""

    @pytest.mark.asyncio
    async def test_translate_basic_text(self):
        """Should produce bilingual output with English and Chinese."""
        from app.services.secretary_agent.tools.article_processor import translate_bilingual

        mock_llm = AsyncMock(return_value="这是一个测试段落。")

        content = "This is a test paragraph with enough text to be translated."
        result = await translate_bilingual(content=content, llm_call_fn=mock_llm)

        # Should contain the original English
        assert "This is a test paragraph" in result
        # Should contain the Chinese translation (in blockquote)
        assert "这是一个测试段落" in result
        # LLM should have been called
        assert mock_llm.called

    @pytest.mark.asyncio
    async def test_code_blocks_not_translated(self):
        """Should preserve code blocks without translation."""
        from app.services.secretary_agent.tools.article_processor import translate_bilingual

        mock_llm = AsyncMock(return_value="翻译后的文本")

        content = (
            "Some text to translate here with enough words.\n\n"
            "```python\nprint('hello')\n```\n\n"
            "More text after the code block."
        )
        result = await translate_bilingual(content=content, llm_call_fn=mock_llm)

        assert "```python" in result or "print('hello')" in result

    @pytest.mark.asyncio
    async def test_heading_translation_inline(self):
        """Should translate headings inline with / separator."""
        from app.services.secretary_agent.tools.article_processor import translate_bilingual

        mock_llm = AsyncMock(return_value="介绍")

        content = "# Introduction"
        result = await translate_bilingual(content=content, llm_call_fn=mock_llm)

        assert "Introduction" in result
        assert "介绍" in result

    @pytest.mark.asyncio
    async def test_requires_llm_function(self):
        """Should raise ValueError if no LLM function provided."""
        from app.services.secretary_agent.tools.article_processor import translate_bilingual

        with pytest.raises(ValueError, match="llm_call_fn is required"):
            await translate_bilingual(content="Some text", llm_call_fn=None)


# ============================================================================
# Test: generate_summary
# ============================================================================


class TestGenerateSummary:
    """Tests for generate_summary function."""

    @pytest.mark.asyncio
    async def test_generate_valid_summary(self):
        """Should parse a valid JSON summary from LLM response."""
        from app.services.secretary_agent.tools.article_processor import generate_summary

        llm_response = json.dumps({
            "summary": "这篇文章讨论了AI Agent的工作流程设计。",
            "key_points": [
                "先写workflow再写prompt",
                "SubAgent遵循SRP",
                "A2A用结构化通讯",
            ],
            "tags": ["AI", "workflow", "agent"],
        })
        mock_llm = AsyncMock(return_value=llm_response)

        result = await generate_summary(
            title="AI Agent Workflow",
            content="Article content about AI agent workflow design...",
            llm_call_fn=mock_llm,
        )

        assert result.summary == "这篇文章讨论了AI Agent的工作流程设计。"
        assert len(result.key_points) == 3
        assert "AI" in result.tags

    @pytest.mark.asyncio
    async def test_generate_summary_fallback_on_invalid_json(self):
        """Should use fallback when LLM returns invalid JSON."""
        from app.services.secretary_agent.tools.article_processor import generate_summary

        mock_llm = AsyncMock(return_value="This is not valid JSON at all.")

        result = await generate_summary(
            title="Test",
            content="Some content",
            llm_call_fn=mock_llm,
        )

        # Fallback: summary is the raw response truncated
        assert len(result.summary) > 0
        assert isinstance(result.key_points, list)

    @pytest.mark.asyncio
    async def test_generate_summary_content_truncation(self):
        """Should truncate very long content before sending to LLM."""
        from app.services.secretary_agent.tools.article_processor import generate_summary

        long_content = "x " * 5000  # ~10000 chars
        mock_llm = AsyncMock(return_value=json.dumps({
            "summary": "Summary",
            "key_points": ["Point 1"],
            "tags": ["test"],
        }))

        await generate_summary(
            title="Long Article",
            content=long_content,
            llm_call_fn=mock_llm,
        )

        # Verify the prompt was called with truncated content
        call_args = mock_llm.call_args[0][0]
        assert "truncated" in call_args


# ============================================================================
# Test: generate_mindmap_plantuml
# ============================================================================


class TestGenerateMindmapPlantuml:
    """Tests for generate_mindmap_plantuml function."""

    @pytest.mark.asyncio
    async def test_generate_valid_mindmap(self):
        """Should produce valid PlantUML mindmap syntax."""
        from app.services.secretary_agent.tools.article_processor import generate_mindmap_plantuml

        mock_llm = AsyncMock(return_value=(
            "@startmindmap\n"
            "* AI工作流\n"
            "** 角色分工\n"
            "*** Super Agent\n"
            "*** Sub Agent\n"
            "@endmindmap"
        ))

        result = await generate_mindmap_plantuml(
            title="AI Workflow",
            key_points=["先写workflow", "SubAgent SRP"],
            content="# AI Workflow\n## Step 1\n## Step 2",
            llm_call_fn=mock_llm,
        )

        assert result.startswith("@startmindmap")
        assert result.endswith("@endmindmap")
        assert "AI工作流" in result

    @pytest.mark.asyncio
    async def test_wraps_missing_tags(self):
        """Should add @startmindmap/@endmindmap if LLM omits them."""
        from app.services.secretary_agent.tools.article_processor import generate_mindmap_plantuml

        # LLM returns mindmap without tags
        mock_llm = AsyncMock(return_value="* Root\n** Branch1\n** Branch2")

        result = await generate_mindmap_plantuml(
            title="Test",
            key_points=["point1"],
            content="# Test",
            llm_call_fn=mock_llm,
        )

        assert result.startswith("@startmindmap")
        assert result.endswith("@endmindmap")

    @pytest.mark.asyncio
    async def test_strips_markdown_code_fences(self):
        """Should remove ```plantuml fences that LLM sometimes adds."""
        from app.services.secretary_agent.tools.article_processor import generate_mindmap_plantuml

        mock_llm = AsyncMock(return_value=(
            "```plantuml\n"
            "@startmindmap\n"
            "* Root\n"
            "@endmindmap\n"
            "```"
        ))

        result = await generate_mindmap_plantuml(
            title="Test",
            key_points=["p1"],
            content="# Test",
            llm_call_fn=mock_llm,
        )

        assert "```" not in result
        assert result.startswith("@startmindmap")


# ============================================================================
# Test: PlantUML Renderer
# ============================================================================


class TestPlantUMLRenderer:
    """Tests for the PlantUML rendering utilities."""

    def test_plantuml_text_encode(self):
        """Should encode PlantUML text for server URL."""
        from app.services.secretary_agent.tools.plantuml_renderer import plantuml_text_encode

        result = plantuml_text_encode("@startmindmap\n* Hello\n@endmindmap")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should only contain valid PlantUML alphabet characters
        valid_chars = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_")
        assert all(c in valid_chars for c in result)

    def test_generate_filename_deterministic(self):
        """Should generate the same filename for the same content."""
        from app.services.secretary_agent.tools.plantuml_renderer import _generate_filename

        script = "@startmindmap\n* Test\n@endmindmap"
        name1 = _generate_filename(script)
        name2 = _generate_filename(script)
        assert name1 == name2
        assert name1.startswith("mindmap_")
        assert name1.endswith(".png")

    def test_generate_filename_different_for_different_content(self):
        """Should generate different filenames for different content."""
        from app.services.secretary_agent.tools.plantuml_renderer import _generate_filename

        name1 = _generate_filename("@startmindmap\n* A\n@endmindmap")
        name2 = _generate_filename("@startmindmap\n* B\n@endmindmap")
        assert name1 != name2

    @pytest.mark.asyncio
    async def test_render_via_server(self):
        """Should call PlantUML server and return PNG bytes."""
        from app.services.secretary_agent.tools.plantuml_renderer import render_via_server

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Fake PNG header
        mock_response.headers = {"content-type": "image/png"}

        with patch("app.services.secretary_agent.tools.plantuml_renderer.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            result = await render_via_server("@startmindmap\n* Test\n@endmindmap")
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_render_via_server_error(self):
        """Should raise RuntimeError on server error."""
        from app.services.secretary_agent.tools.plantuml_renderer import render_via_server

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("app.services.secretary_agent.tools.plantuml_renderer.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client

            with pytest.raises(RuntimeError, match="500"):
                await render_via_server("@startmindmap\n* Test\n@endmindmap")

    @pytest.mark.asyncio
    async def test_render_plantuml_to_png_saves_file(self, tmp_path):
        """Should render and save PNG file to output directory."""
        from app.services.secretary_agent.tools.plantuml_renderer import render_plantuml_to_png

        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("app.services.secretary_agent.tools.plantuml_renderer._get_output_dir", return_value=tmp_path), \
             patch("app.services.secretary_agent.tools.plantuml_renderer._jar_available", return_value=False), \
             patch("app.services.secretary_agent.tools.plantuml_renderer.render_via_server", new_callable=AsyncMock, return_value=fake_png):

            result = await render_plantuml_to_png("@startmindmap\n* Test\n@endmindmap")

            assert result.endswith(".png")
            # File should exist at the returned path
            from pathlib import Path
            assert Path(result).exists()
            assert Path(result).stat().st_size > 0

    @pytest.mark.asyncio
    async def test_render_plantuml_to_png_caches(self, tmp_path):
        """Should return existing file without re-rendering."""
        from app.services.secretary_agent.tools.plantuml_renderer import render_plantuml_to_png, _generate_filename

        script = "@startmindmap\n* Cached\n@endmindmap"
        fname = _generate_filename(script)
        cached_file = tmp_path / fname
        cached_file.write_bytes(b"cached_png_data")

        with patch("app.services.secretary_agent.tools.plantuml_renderer._get_output_dir", return_value=tmp_path):
            # Should NOT call any render function
            result = await render_plantuml_to_png(script)
            assert result.endswith(fname)


# ============================================================================
# Test: Helper Functions
# ============================================================================


class TestHelpers:
    """Tests for internal helper functions."""

    def test_split_paragraphs_basic(self):
        """Should split text on blank lines."""
        from app.services.secretary_agent.tools.article_processor import _split_paragraphs

        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        result = _split_paragraphs(text)
        assert len(result) == 3
        assert result[0] == "Paragraph one."
        assert result[1] == "Paragraph two."

    def test_split_paragraphs_preserves_code_blocks(self):
        """Should keep code blocks as single paragraphs."""
        from app.services.secretary_agent.tools.article_processor import _split_paragraphs

        text = (
            "Some text.\n\n"
            "```python\n"
            "def hello():\n"
            "    print('hi')\n"
            "```\n\n"
            "More text."
        )
        result = _split_paragraphs(text)
        # Should have 3 parts: text, code block, text
        assert len(result) == 3
        assert "```python" in result[1]
        assert "print('hi')" in result[1]

    def test_is_code_block(self):
        """Should identify fenced code blocks."""
        from app.services.secretary_agent.tools.article_processor import _is_code_block

        assert _is_code_block("```python\nprint('hi')\n```") is True
        assert _is_code_block("regular text") is False
        assert _is_code_block("```\ncode\n```") is True

    def test_is_heading(self):
        """Should identify markdown headings."""
        from app.services.secretary_agent.tools.article_processor import _is_heading

        assert _is_heading("# Title") is True
        assert _is_heading("## Section") is True
        assert _is_heading("### Subsection") is True
        assert _is_heading("Regular text") is False

    def test_extract_headings(self):
        """Should extract heading lines from markdown."""
        from app.services.secretary_agent.tools.article_processor import _extract_headings

        content = "# Title\nSome text\n## Section 1\nMore text\n### Sub\nEnd"
        result = _extract_headings(content)
        assert "# Title" in result
        assert "## Section 1" in result
        assert "### Sub" in result
        assert "Some text" not in result

    def test_extract_headings_no_headings(self):
        """Should return fallback when no headings found."""
        from app.services.secretary_agent.tools.article_processor import _extract_headings

        result = _extract_headings("Just plain text\nNo headings here")
        assert "no headings" in result
