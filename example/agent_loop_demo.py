#!/usr/bin/env python3
"""
Agent Loop demo with real LLM interaction + file tools.

This script demonstrates a minimal "LLM -> tool call -> observation -> LLM"
loop with workspace-safe file operations. It can handle general tasks such as:
- writing a blog draft
- translating an English article into Chinese
- reading and rewriting files

Quick start (OpenAI-compatible endpoint):
  # .env:
  # LLM_BASE_URL=https://api.openai.com/v1
  # LLM_API_KEY=your_key
  # LLM_MODEL=gpt-4o-mini
  python scripts/agent_loop_demo.py --task \
    "Translate docs/input_en.md to Chinese and save to docs/output_zh.md"

Example with custom API base/model:
  # .env:
  # LLM_BASE_URL=https://api.openai.com/v1
  # LLM_MODEL=gpt-4o-mini
  # LLM_API_KEY=your_key
  # LLM_TEMPERATURE=0.2
  # LLM_STREAM=1
  # LLM_SYSTEM_PROMPT_TEMPLATE=/absolute/path/to/prompt.txt (optional)
  python scripts/agent_loop_demo.py --task "Write a short blog about Agent Loop to demo/blog.md"

Offline smoke test:
  python scripts/agent_loop_demo.py --task "list files in ."
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import httpx

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - depends on local env
    OpenAI = None  # type: ignore[assignment]


@dataclass
class ToolResult:
    for_llm: str
    for_user: str
    ok: bool = True


class AgentTools:
    """Workspace-bounded file tools."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def _safe_path(self, raw_path: str) -> Path:
        candidate = (self.workspace / raw_path).resolve()
        if not str(candidate).startswith(str(self.workspace)):
            raise ValueError(
                f"Path escapes workspace: {raw_path!r}. Workspace={self.workspace}"
            )
        return candidate

    def list_dir(self, raw_path: str = ".") -> ToolResult:
        try:
            target = self._safe_path(raw_path)
            if not target.exists():
                return ToolResult(
                    for_llm=f"Directory not found: {raw_path}",
                    for_user=f"Directory not found: `{raw_path}`",
                    ok=False,
                )
            if not target.is_dir():
                return ToolResult(
                    for_llm=f"Not a directory: {raw_path}",
                    for_user=f"Not a directory: `{raw_path}`",
                    ok=False,
                )

            items = sorted(p.name for p in target.iterdir())
            preview = "\n".join(items[:200]) or "(empty)"
            return ToolResult(
                for_llm=f"Listed {len(items)} entries from {raw_path}\n{preview}",
                for_user=f"Listed `{raw_path}` ({len(items)} entries).",
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                for_llm=f"list_dir failed: {exc}",
                for_user=f"list failed: {exc}",
                ok=False,
            )

    def read_file(self, raw_path: str) -> ToolResult:
        try:
            target = self._safe_path(raw_path)
            if not target.exists():
                return ToolResult(
                    for_llm=f"File not found: {raw_path}",
                    for_user=f"File not found: `{raw_path}`",
                    ok=False,
                )
            if not target.is_file():
                return ToolResult(
                    for_llm=f"Not a file: {raw_path}",
                    for_user=f"Not a file: `{raw_path}`",
                    ok=False,
                )
            content = target.read_text(encoding="utf-8")
            file_max_len = 10 * 1024 * 1024
            clipped = content[:file_max_len]
            if len(content) > len(clipped):
                clipped += f"\n... [truncated] {len(content) - file_max_len}"
            return ToolResult(
                for_llm=clipped,
                for_user=f"Read `{raw_path}` ({len(content)} chars).",
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                for_llm=f"read_file failed: {exc}",
                for_user=f"read failed: {exc}",
                ok=False,
            )

    def write_file(self, raw_path: str, content: str) -> ToolResult:
        try:
            target = self._safe_path(raw_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return ToolResult(
                for_llm=f"Wrote {len(content)} chars to {raw_path}",
                for_user=f"Wrote `{raw_path}` ({len(content)} chars).",
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                for_llm=f"write_file failed: {exc}",
                for_user=f"write failed: {exc}",
                ok=False,
            )

    def append_file(self, raw_path: str, content: str) -> ToolResult:
        try:
            target = self._safe_path(raw_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            prefix = "" if not target.exists() else "\n"
            target.write_text(
                target.read_text(encoding="utf-8") + prefix + content,
                encoding="utf-8",
            )
            return ToolResult(
                for_llm=f"Appended {len(content)} chars to {raw_path}",
                for_user=f"Appended to `{raw_path}` ({len(content)} chars).",
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                for_llm=f"append_file failed: {exc}",
                for_user=f"append failed: {exc}",
                ok=False,
            )

    def get_current_datetime(self) -> ToolResult:
        try:
            now = datetime.now().astimezone()
            human_text = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
            iso_text = now.isoformat()
            return ToolResult(
                for_llm=(
                    "Current local date and time:\n"
                    f"- human_readable: {human_text}\n"
                    f"- iso_8601: {iso_text}"
                ),
                for_user=f"Current date/time: {human_text}",
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                for_llm=f"get_current_datetime failed: {exc}",
                for_user=f"date/time lookup failed: {exc}",
                ok=False,
            )


@dataclass
class Action:
    kind: str  # "tool" | "final"
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    final_text: Optional[str] = None


class ShortTermMemory:
    """In-memory rolling window for recent conversation/tool observations."""

    def __init__(self, max_items: int = 20) -> None:
        self.max_items = max(1, max_items)
        self.items: List[Dict[str, str]] = []

    def reset(self) -> None:
        self.items = []

    def add(self, role: str, content: str) -> None:
        self.items.append({"role": role, "content": content[:4000]})
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    def render_for_prompt(self) -> str:
        if not self.items:
            return "(empty)"
        lines = []
        for idx, item in enumerate(self.items, start=1):
            lines.append(f"{idx}. [{item['role']}] {item['content']}")
        return "\n".join(lines)


class LongTermMemory:
    """Persisted memory entries shared across runs."""

    def __init__(self, file_path: Path, max_items: int = 200) -> None:
        self.file_path = file_path
        self.max_items = max(10, max_items)
        self.items: List[Dict[str, str]] = []
        self._load()

    def _load(self) -> None:
        try:
            if self.file_path.exists():
                raw = json.loads(self.file_path.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    self.items = [x for x in raw if isinstance(x, dict)][-self.max_items :]
        except Exception:  # noqa: BLE001
            self.items = []

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(self.items[-self.max_items :], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, category: str, content: str) -> None:
        entry = {
            "category": category,
            "content": content.strip()[:1000],
        }
        self.items.append(entry)
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]
        self._save()

    def recall(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        q_terms = set(re.findall(r"[a-zA-Z0-9_\-]+", query.lower()))
        if not q_terms:
            return self.items[-top_k:]

        scored: List[tuple[int, Dict[str, str]]] = []
        for item in self.items:
            content = item.get("content", "").lower()
            score = sum(1 for t in q_terms if t in content)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in scored[:top_k]] or self.items[-top_k:]


SYSTEM_PROMPT = """You are an agent running in a local workspace.
You can choose tools to complete the user's task.

Available tools:
1) list_dir(path: string)
2) read_file(path: string)
3) write_file(path: string, content: string)
4) append_file(path: string, content: string)
5) get_current_datetime()

Rules:
- Paths are relative to workspace.
- Prefer reading source before writing transformed content.
- For translation tasks: preserve structure/format (headings, lists, code blocks).
- For blog writing tasks: write complete markdown to target path.
- If the content is long, do NOT send the whole document in one response.
- For long files, use multiple turns:
  1. write_file(path, first chunk)
  2. append_file(path, next chunk)
  3. repeat append_file until complete
  4. then return final
- Keep each tool call payload reasonably small.
- Never output explanatory prose before or after the JSON object.
- When done, return a concise final result.

Response format (STRICT JSON only, no markdown fences, exactly ONE JSON object per response):
If you need a tool:
{"action":"tool","tool_name":"read_file","tool_args":{"path":"input.md"}}

For current time/date:
{"action":"tool","tool_name":"get_current_datetime","tool_args":{}}

If done:
{"action":"final","final_text":"Completed. Wrote output to ..."}
"""


class LLMClient:
    """OpenAI-compatible client via official openai SDK."""

    def __init__(
        self,
        api_base: str,
        model: str,
        api_key: str,
        temperature: float = 0.2,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.client: Optional[OpenAI] = None
        if OpenAI is None:
            raise RuntimeError(
                "openai package is not installed. "
                "Install it with: pip install openai"
            )
        if not self.api_key:
            raise RuntimeError(
                "LLM_API_KEY is required. "
                "Set it in .env or env var."
            )
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
            default_headers={"X-Api-Key": self.api_key},
            # For self-hosted endpoints with self-signed certificates.
            http_client=httpx.Client(verify=False, timeout=90.0),
        )

    def complete(self, messages: List[Dict[str, str]]) -> str:
        return self._openai_compatible_complete(messages)

    def _openai_compatible_complete(self, messages: List[Dict[str, str]]) -> str:
        return self.complete_with_options(messages, stream=False, on_token=None)

    def complete_with_options(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> str:
        if self.client is None:
            raise RuntimeError("LLM client is not initialized.")
        if not stream:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(f"LLM request failed: {exc}") from exc

            content = response.choices[0].message.content
            return content or ""

        chunks: List[str] = []
        try:
            stream_resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                stream=True,
            )
            for chunk in stream_resp:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                text = delta.content or ""
                if not text:
                    continue
                chunks.append(text)
                if on_token is not None:
                    on_token(text)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"LLM stream request failed: {exc}") from exc

        return "".join(chunks)

def extract_json_object(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        # handle fenced output
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Fast path: a single JSON object.
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Robust path: tolerate multiple JSON objects in one response and
    # select the first object that looks like an action payload.
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(text):
        # Move to next object start.
        while idx < len(text) and text[idx] != "{":
            idx += 1
        if idx >= len(text):
            break
        try:
            obj, next_idx = decoder.raw_decode(text, idx)
            if isinstance(obj, dict) and "action" in obj:
                return obj
            idx = max(next_idx, idx + 1)
        except json.JSONDecodeError:
            idx += 1

    raise json.JSONDecodeError("No valid JSON action object found", text, 0)


def recover_action_from_text(raw: str, workspace: Optional[Path] = None) -> Optional[Action]:
    """
    Best-effort recovery for non-JSON model outputs.

    Some self-hosted models occasionally echo tool observations like:
      TOOL_RESULT::write_file
      Wrote 13034 bytes to k8s-authn-authz.md
    In this case, we treat it as successful completion instead of failing.
    """
    text = raw.strip()
    if not text:
        return None

    m = re.search(r"TOOL_RESULT::([a-zA-Z0-9_]+)", text)
    tool_name = m.group(1) if m else ""

    if tool_name in {"write_file", "append_file"}:
        path_match = re.search(r"to\s+([^\s]+)", text, flags=re.IGNORECASE)
        path_hint = path_match.group(1) if path_match else "target file"
        path_hint = path_hint.strip().strip("`'\"")
        if path_hint.endswith("."):
            path_hint = path_hint[:-1]

        # Guard against false-positive completions: only report success if
        # the file actually exists in workspace.
        if workspace and path_hint and path_hint != "target file":
            try:
                candidate = (workspace / path_hint).resolve()
                if not str(candidate).startswith(str(workspace)):
                    return None
                if not candidate.exists():
                    return None
            except Exception:  # noqa: BLE001
                return None

        return Action(
            kind="final",
            final_text=f"Completed. Output written to {path_hint}.",
        )

    if "completed" in text.lower() or "done" in text.lower():
        return Action(kind="final", final_text=text[:500])

    return None


def infer_expected_output_paths(task: str) -> List[str]:
    """Infer likely output paths from natural language task."""
    patterns = [
        r"\binto\s+([^\s,;]+)",
        r"\bto\s+([^\s,;]+)",
        r"\bsave\s+(?:it\s+)?to\s+([^\s,;]+)",
        r"\bwrite\s+(?:it\s+)?to\s+([^\s,;]+)",
        r"\boutput\s+to\s+([^\s,;]+)",
    ]
    hits: List[str] = []
    for pat in patterns:
        for match in re.findall(pat, task, flags=re.IGNORECASE):
            candidate = str(match).strip().strip("`'\"")
            if candidate.endswith("."):
                candidate = candidate[:-1]
            if "/" in candidate or "." in candidate:
                hits.append(candidate)
    # Deduplicate while preserving order.
    seen = set()
    out: List[str] = []
    for item in hits:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


class AgentLoopDemo:
    def __init__(
        self,
        workspace: Path,
        llm: LLMClient,
        max_iterations: int = 100,
        verbose: bool = False,
        stream_output: bool = True,
        debug: bool = False,
        system_prompt: str = SYSTEM_PROMPT,
        short_memory_window: int = 20,
        long_memory_top_k: int = 5,
    ):
        self.workspace = workspace.resolve()
        self.llm = llm
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.stream_output = stream_output
        self.debug = debug
        self.system_prompt = system_prompt
        self.tools = AgentTools(self.workspace)
        self.messages: List[Dict[str, Any]] = []
        self._written_paths: set[str] = set()
        self.short_memory = ShortTermMemory(max_items=short_memory_window)
        self.long_memory = LongTermMemory(
            file_path=self.workspace / "memory" / "long_term_memory.json",
        )
        self.long_memory_top_k = max(1, long_memory_top_k)
        self.current_plan: str = ""

    def _debug(self, msg: str) -> None:
        if self.debug:
            print(f"[debug] {msg}")

    def _path_exists_in_workspace(self, raw_path: str) -> bool:
        try:
            candidate = (self.workspace / raw_path).resolve()
            if not str(candidate).startswith(str(self.workspace)):
                return False
            return candidate.exists()
        except Exception:  # noqa: BLE001
            return False

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> ToolResult:
        if name == "list_dir":
            return self.tools.list_dir(args.get("path", "."))
        if name == "read_file":
            return self.tools.read_file(args["path"])
        if name == "write_file":
            return self.tools.write_file(args["path"], args.get("content", ""))
        if name == "append_file":
            return self.tools.append_file(args["path"], args.get("content", ""))
        if name == "get_current_datetime":
            return self.tools.get_current_datetime()
        return ToolResult(
            for_llm=f"Unknown tool: {name}",
            for_user=f"Unknown tool: {name}",
            ok=False,
        )

    def _create_plan(self, task: str, expected_outputs: List[str]) -> str:
        plan_prompt = (
            "Create a concise execution plan (3-8 bullets) for this task.\n"
            f"Task: {task}\n"
            f"Expected outputs: {expected_outputs or ['(none)']}\n"
            "Rules: focus on tool usage and validation steps."
        )
        messages = [
            {"role": "system", "content": "You are a planning module. Output plain text bullets only."},
            {"role": "user", "content": plan_prompt},
        ]
        try:
            plan = self.llm.complete_with_options(messages, stream=False, on_token=None).strip()
        except Exception as exc:  # noqa: BLE001
            plan = f"- Planning fallback due to error: {exc}\n- Try read/list first, then write output, then verify file exists."
        return plan[:3000]

    def _build_llm_messages(self) -> List[Dict[str, str]]:
        recalled = self.long_memory.recall(
            query=self.messages[0]["content"] if self.messages else "",
            top_k=self.long_memory_top_k,
        )
        recalled_text = "\n".join(
            f"- [{item.get('category','note')}] {item.get('content','')}" for item in recalled
        ) or "(none)"
        prompt_messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "system",
                "content": f"Workspace root: {self.workspace}",
            },
            {
                "role": "system",
                "content": (
                    "Execution plan (planning module):\n"
                    f"{self.current_plan or '(no plan)'}"
                ),
            },
            {
                "role": "system",
                "content": (
                    "Short-term memory (recent turns):\n"
                    f"{self.short_memory.render_for_prompt()}"
                ),
            },
            {
                "role": "system",
                "content": (
                    "Long-term memory recall:\n"
                    f"{recalled_text}"
                ),
            },
        ]
        for msg in self.messages:
            role = msg["role"]
            if role in {"user", "assistant"}:
                prompt_messages.append({"role": role, "content": msg["content"]})
            elif role == "tool":
                tool_name = msg.get("name", "unknown")
                prompt_messages.append(
                    {
                        # Feed tool observations back as user-side execution context
                        # so the next request does not end with an assistant message.
                        "role": "user",
                        "content": (
                            "Tool result from the previous step.\n"
                            f"Tool: {tool_name}\n"
                            f"Observation:\n{msg.get('content', '')[:12000]}"
                        ),
                    }
                )
        return prompt_messages

    def _normalize_action(self, payload: Dict[str, Any]) -> Action:
        action = str(payload.get("action", "")).strip().lower()
        if action == "final":
            return Action(kind="final", final_text=str(payload.get("final_text", "Task finished.")))
        if action == "tool":
            tool_name = str(payload.get("tool_name", "")).strip()
            tool_args = payload.get("tool_args", {})
            if not isinstance(tool_args, dict):
                tool_args = {}
            return Action(kind="tool", tool_name=tool_name, tool_args=tool_args)
        return Action(
            kind="final",
            final_text="Invalid LLM action format. Stopped safely.",
        )

    def run_task(self, task: str) -> str:
        self.messages = [{"role": "user", "content": task}]
        self._written_paths = set()
        self.short_memory.reset()
        self.short_memory.add("user", task)
        expected_outputs = infer_expected_output_paths(task)
        if expected_outputs:
            self._debug(f"expected output candidates: {expected_outputs}")
        self.current_plan = self._create_plan(task, expected_outputs)
        self._debug(f"plan:\n{self.current_plan}")

        for iteration in range(self.max_iterations):
            if iteration > 0:
                print("")
            llm_messages = self._build_llm_messages()
            if self.verbose:
                prompt_dump = json.dumps(llm_messages, ensure_ascii=False, indent=2)
                print(f"## iteration {iteration + 1}")
                print(f"* request:\n{prompt_dump}")
            else:
                print(f"[iteration {iteration + 1}]")
            if self.stream_output:
                print("llm> ", end="", flush=True)
            try:
                raw = self.llm.complete_with_options(
                    llm_messages,
                    stream=self.stream_output,
                    on_token=(lambda token: print(token, end="", flush=True))
                    if self.stream_output
                    else None,
                )
            except Exception as exc:  # noqa: BLE001
                if self.stream_output:
                    print("")
                if self.verbose:
                    print(f"* error: LLM request failed: {exc}")
                return f"Stopped: LLM request failed: {exc}"
            if self.stream_output:
                print("")
            if self.verbose:
                print(f"* response:\n{raw}")

            try:
                payload = extract_json_object(raw)
            except Exception as exc:  # noqa: BLE001
                self.messages.append({"role": "assistant", "content": raw})
                self.short_memory.add("assistant_raw", raw[:1000])
                recovered = recover_action_from_text(raw, workspace=self.workspace)
                if recovered and recovered.kind == "final":
                    # Final result must be evidence-based when output path is expected.
                    if expected_outputs:
                        missing = [p for p in expected_outputs if not self._path_exists_in_workspace(p)]
                        if missing:
                            self._debug(
                                f"recovered final rejected, missing expected files: {missing}"
                            )
                        else:
                            self.long_memory.add(
                                "task_result",
                                f"task={task}; final={recovered.final_text or ''}",
                            )
                            return recovered.final_text or "Task finished."
                    else:
                        self.long_memory.add(
                            "task_result",
                            f"task={task}; final={recovered.final_text or ''}",
                        )
                        return recovered.final_text or "Task finished."
                # Ask model to correct format and continue next iteration.
                self.messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous reply was invalid. Return exactly ONE JSON object "
                            "with either action=tool or action=final. "
                            "Do not output TOOL_RESULT text or multiple JSON objects. "
                            "If you are writing a long file, split it into smaller chunks using "
                            "write_file for the first chunk and append_file for later chunks."
                        ),
                    }
                )
                if self.verbose:
                    print(f"* error: invalid JSON from model, retrying: {exc}")
                    preview = raw if len(raw) <= 1200 else raw[:1200] + "\n... [truncated]"
                    print(
                        "* note: tool call not executed because the response could not be parsed "
                        "into one complete JSON action."
                    )
                    print(f"* raw_response_preview:\n{preview}")
                continue

            action = self._normalize_action(payload)
            if self.verbose:
                print(f"* parsed_action:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")
            if action.kind == "tool":
                assistant_summary = {
                    "action": "tool",
                    "tool_name": action.tool_name,
                    "tool_args": action.tool_args,
                }
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(assistant_summary, ensure_ascii=False),
                    }
                )
                self.short_memory.add(
                    "assistant_action",
                    json.dumps(assistant_summary, ensure_ascii=False)[:1000],
                )
            else:
                self.messages.append({"role": "assistant", "content": raw})
                self.short_memory.add("assistant_raw", raw[:1000])
            if action.kind == "final":
                # Hard guarantee: if output path is expected, verify files exist before success.
                if expected_outputs:
                    missing = [p for p in expected_outputs if not self._path_exists_in_workspace(p)]
                    if missing:
                        self._debug(f"final rejected, missing expected files: {missing}")
                        self.messages.append(
                            {
                                "role": "user",
                                "content": (
                                    "Do not finish yet. These required output files are still missing: "
                                    + ", ".join(missing)
                                    + ". Use write_file/append_file to create them, then return final JSON."
                                ),
                            }
                        )
                        continue
                self.long_memory.add(
                    "task_result",
                    f"task={task}; final={action.final_text or ''}",
                )
                return action.final_text or "Task finished."

            assert action.tool_name is not None
            assert action.tool_args is not None
            if self.verbose:
                print(
                    f"* tool_call: {action.tool_name} args={json.dumps(action.tool_args, ensure_ascii=False)}"
                )

            result = self._execute_tool(action.tool_name, action.tool_args)
            self.short_memory.add(
                "tool_result",
                f"{action.tool_name}: {result.for_llm[:800]}",
            )
            if action.tool_name in {"write_file", "append_file"}:
                written_path = str(action.tool_args.get("path", "")).strip()
                if written_path:
                    self._written_paths.add(written_path)
                    self._debug(f"tracked written path: {written_path}")
                    self.long_memory.add(
                        "written_file",
                        f"path={written_path}; status={'ok' if result.ok else 'failed'}",
                    )
            self.messages.append(
                {
                    "role": "tool",
                    "name": action.tool_name,
                    "content": result.for_llm,
                }
            )

            if self.verbose:
                print(f"* tool_result: {result.for_user}")

        return f"Stopped: reached max iterations ({self.max_iterations})."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demo of an Agent Loop with file read/write tools. LLM settings come from .env."
    )
    parser.add_argument(
        "--task",
        type=str,
        default="",
        help="Single task to run. If empty, use --interactive.",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root for safe file tools (default: current directory).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=60,
        help="Maximum loop iterations per task.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive mode.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each tool call and observation.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug logs for parser and completion checks.",
    )
    return parser


def run_interactive(agent: AgentLoopDemo) -> int:
    print("Agent Loop demo (interactive mode). Type 'exit' to quit.")
    print("Examples:")
    print("  Translate content/tech/input_en.md to Chinese and save to content/tech/output_zh.md")
    print("  Write a blog draft about agent loop to content/tech/tech_demo.md")
    print("  Read README.md and write a Chinese summary to demo/readme_zh.md")
    print("")
    while True:
        try:
            task = input("task> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            return 0

        if not task:
            continue
        if task.lower() in {"exit", "quit"}:
            return 0

        output = agent.run_task(task)
        print(output)


def load_env_file(env_path: Path) -> None:
    """Load KEY=VALUE pairs from .env into process env (non-destructive)."""
    if not env_path.exists() or not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def load_system_prompt(default_prompt: str) -> str:
    template_path = os.environ.get("LLM_SYSTEM_PROMPT_TEMPLATE", "").strip()
    if not template_path:
        return default_prompt
    p = Path(template_path).expanduser()
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return default_prompt


def main() -> int:
    load_env_file(Path(".env"))
    parser = build_parser()
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    api_base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini").strip()
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    temperature_raw = os.environ.get("LLM_TEMPERATURE", "0.2").strip()
    try:
        temperature = float(temperature_raw)
    except ValueError:
        temperature = 0.2
    stream_output = env_bool("LLM_STREAM", True)
    system_prompt = load_system_prompt(SYSTEM_PROMPT)
    short_memory_window_raw = os.environ.get("SHORT_MEMORY_WINDOW", "20").strip()
    long_memory_top_k_raw = os.environ.get("LONG_MEMORY_TOP_K", "5").strip()
    try:
        short_memory_window = int(short_memory_window_raw)
    except ValueError:
        short_memory_window = 20
    try:
        long_memory_top_k = int(long_memory_top_k_raw)
    except ValueError:
        long_memory_top_k = 5

    llm = LLMClient(
        api_base=api_base,
        model=model,
        api_key=api_key,
        temperature=temperature,
    )

    agent = AgentLoopDemo(
        workspace=workspace,
        llm=llm,
        max_iterations=max(1, args.max_iterations),
        verbose=args.verbose,
        stream_output=stream_output,
        debug=args.debug,
        system_prompt=system_prompt,
        short_memory_window=short_memory_window,
        long_memory_top_k=long_memory_top_k,
    )

    if args.interactive:
        return run_interactive(agent)

    if not args.task:
        parser.print_help()
        return 1

    output = agent.run_task(args.task)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
