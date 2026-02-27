# Change Proposal: Translation Agent

## Why

Users need to consume English content (articles, docs, PDFs) in Chinese with not only a translation but also explanation and summary to aid understanding. A dedicated translation agent that accepts URL, PDF, or text/markdown input and returns translated content plus explanation and summary fills this gap and can reuse existing fetch/PDF handling from the article pipeline.

## What Changes

- **New Translation Agent**: An AI agent (or tool/flow) that:
  - Accepts input from: **URL** (fetched first), **PDF** (file or URL), **text/markdown files** (e.g. `.txt`, `.md`) — text files may require upload.
  - Produces: **Markdown** for the translated content (English → Chinese), plus **explanation** and **summary** of the content.
- **Input handling**: Fetch URL content (reuse or align with article pipeline), accept PDF (file upload or URL), accept uploaded text/markdown files.
- **Output format**: Structured response with at least: translated markdown, explanation, summary. Support **two output modes**: **Chinese only** (translation only) and **bilingual** (each segment: original English + Chinese translation). **Real-time streaming** of translation output is required. The full result SHALL be available as a **single markdown file** that the user can **download**, and the frontend SHALL **render that markdown as HTML** on the translation page.
- **API**: New endpoint(s) or integration point for translation (e.g. under `/api/v1/translation`) supporting both non-streaming (JSON) and streaming (e.g. SSE) modes.

## Capabilities

### New Capabilities

- `translation-agent`: Translates English content from URL, PDF, or text/markdown into Chinese; returns markdown translation plus explanation and summary. Covers input types (URL fetch, PDF, file upload), output schema, and any storage/export of results.

### Modified Capabilities

- *(None)* — Translation is a new capability. If later the Personal Secretary is extended to invoke this (e.g. via a tool), that can be a separate change.

## Impact

- **Backend**: New service or agent module for translation (and possibly new routes), reuse of existing fetch/PDF extraction where applicable; possible file-upload support for `.txt`/`.md`.
- **Frontend**: UI to supply URL, upload PDF/text files; display translated result as **HTML** (markdown rendered on the page); offer **download as .md file**; support real-time streaming so content appears progressively (new view or integration in existing flows).
- **Dependencies**: Existing LLM and article fetch/PDF stack; no new external services required unless design chooses otherwise.
- **APIs**: New translation endpoint(s); authentication consistent with existing API (e.g. JWT).
