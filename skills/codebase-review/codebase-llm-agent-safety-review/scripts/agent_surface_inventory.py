#!/usr/bin/env python3
"""Read-only inventory for LLM, agent, tool, retrieval, and memory surfaces.

The script scans local text files, redacts secret-like values in previews, and
does not call the network or execute project code. Use it as a review starting
point, then verify findings manually.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    ".cache",
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".cs",
    ".go",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".mjs",
    ".php",
    ".properties",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

CONFIG_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "poetry.lock",
    "uv.lock",
    "go.mod",
    "Cargo.toml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "agents.json",
    "mcp.json",
    "marketplace.json",
    "plugin.json",
    "openapi.json",
    "openapi.yaml",
    "openapi.yml",
}

SECRET_NAME = r"[A-Za-z0-9_.-]*(?:secret|token|password|passwd|api[_-]?key|client[_-]?secret|private[_-]?key|credential)[A-Za-z0-9_.-]*"


@dataclass
class Match:
    category: str
    label: str
    path: str
    line: int
    preview: str


@dataclass
class Inventory:
    root: str
    model_calls: list[Match]
    prompt_construction: list[Match]
    tool_definitions: list[Match]
    mcp_plugin_configs: list[Match]
    retrieval_sources: list[Match]
    memory_stores: list[Match]
    file_network_code_tools: list[Match]
    approval_gates: list[Match]
    output_sinks: list[Match]
    sensitive_data_signals: list[Match]
    candidate_config_files: list[str]


PATTERNS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "model_calls": [
        ("openai-client", re.compile(r"\b(OpenAI|AsyncOpenAI|chat\.completions|responses\.create|responses\.stream|beta\.threads|assistants)\b")),
        ("anthropic-client", re.compile(r"\b(Anthropic|messages\.create|claude|bedrock-runtime)\b", re.I)),
        ("llm-framework", re.compile(r"\b(langchain|llamaindex|semantic[_-]?kernel|haystack|litellm|autogen|crewai|openrouter)\b", re.I)),
        ("model-field", re.compile(r"(?i)\b(model|model_name|deployment_name)\b\s*[:=]\s*['\"][A-Za-z0-9_.:/-]+")),
    ],
    "prompt_construction": [
        ("system-prompt", re.compile(r"(?i)\b(system_prompt|system message|developer_prompt|instruction|instructions)\b")),
        ("prompt-template", re.compile(r"(?i)\b(prompt_template|ChatPromptTemplate|PromptTemplate|render_prompt|build_prompt|messages\s*=)\b")),
        ("role-message", re.compile(r"['\"]role['\"]\s*:\s*['\"](?:system|developer|user|assistant|tool)['\"]")),
    ],
    "tool_definitions": [
        ("tool-schema", re.compile(r"(?i)\b(tools?|function_call|tool_choice|input_schema|parameters|zod|json_schema)\b")),
        ("agent-tool", re.compile(r"(?i)\b(@tool|Tool\(|StructuredTool|BaseTool|tool_calls?|execute_tool|invoke_tool|tool_router)\b")),
        ("action-registry", re.compile(r"(?i)\b(actions?|capabilities|permissions|allowlist|denylist|whitelist|blacklist)\b")),
    ],
    "mcp_plugin_configs": [
        ("mcp-server", re.compile(r"(?i)\b(mcpServers|mcp_server|Model Context Protocol|stdio|sse|serverUrl)\b")),
        ("plugin-config", re.compile(r"(?i)\b(plugin\.json|marketplace|connector|plugins?|manifest|trusted|trust_level)\b")),
        ("codex-agents", re.compile(r"(?i)\b(\.codex-plugin|\.agents|agents/openai\.yaml|skills/)\b")),
    ],
    "retrieval_sources": [
        ("vector-store", re.compile(r"(?i)\b(vector(store|_store)?|embedding|embed_documents|similarity_search|pinecone|weaviate|qdrant|chroma|faiss|milvus)\b")),
        ("retriever", re.compile(r"(?i)\b(retriever|retrieve|rag|document_loader|loader|index|chunk|rerank|search)\b")),
        ("upload-source", re.compile(r"(?i)\b(upload|attachment|file_input|multipart|crawler|scrape|web_search)\b")),
    ],
    "memory_stores": [
        ("memory", re.compile(r"(?i)\b(memory|chat_history|conversation_history|checkpoint|thread_state|session_state|summar(y|ize)|compaction)\b")),
        ("cache-or-log", re.compile(r"(?i)\b(cache|trace|telemetry|analytics|event_log|audit_log|transcript)\b")),
        ("storage", re.compile(r"(?i)\b(redis|sqlite|postgres|s3|dynamodb|firestore|supabase|localStorage|indexedDB)\b")),
    ],
    "file_network_code_tools": [
        ("file-access", re.compile(r"\b(open\s*\(|readFile|writeFile|Path\(|glob\(|fs\.|os\.remove|shutil\.rmtree)\b")),
        ("network-access", re.compile(r"\b(fetch\s*\(|axios\.|requests\.(get|post|put|delete)|urllib\.request|httpx\.|curl\b|webhook)\b")),
        ("code-exec", re.compile(r"\b(shell=True|subprocess\.(run|Popen|call)|os\.system|child_process\.(exec|spawn)|eval\s*\(|exec\s*\(|Function\s*\()\b")),
        ("browser", re.compile(r"(?i)\b(playwright|puppeteer|selenium|browser|page\.goto|click\(|screenshot)\b")),
    ],
    "approval_gates": [
        ("approval", re.compile(r"(?i)\b(approval|approve|confirm|human[-_ ]?in[-_ ]?the[-_ ]?loop|review_required|requires_review)\b")),
        ("dry-run", re.compile(r"(?i)\b(dry_run|dry-run|preview|plan_only|no_execute|read_only|readonly)\b")),
        ("destructive-action", re.compile(r"(?i)\b(delete|destroy|overwrite|merge|deploy|publish|send_email|purchase|charge|grant|revoke)\b")),
    ],
    "output_sinks": [
        ("message-sink", re.compile(r"(?i)\b(slack|teams|email|send_mail|smtp|webhook|ticket|jira|github|comment|pull request|issue)\b")),
        ("file-or-report", re.compile(r"(?i)\b(report|export|download|write_text|writeFile|save|artifact|output_dir)\b")),
        ("external-api", re.compile(r"(?i)\b(api\.|client\.|post\(|put\(|publish|notify|callback_url|redirect_url)\b")),
    ],
    "sensitive_data_signals": [
        ("secret-like-name", re.compile(rf"(?i)\b{SECRET_NAME}\b")),
        ("tenant-scope", re.compile(r"(?i)\b(tenant|workspace|organization|organisation|account_id|org_id|project_id|user_id)\b")),
        ("private-data", re.compile(r"(?i)\b(credentials?|secrets?|private|confidential|pii|customer|billing|financial|source_code)\b")),
    ],
}


def is_text_candidate(path: Path) -> bool:
    if path.name in CONFIG_NAMES:
        return True
    if path.name.startswith(".env"):
        return True
    return path.suffix in TEXT_SUFFIXES


def iter_files(root: Path, max_bytes: int) -> Iterable[Path]:
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            path = Path(current_root) / filename
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            if is_text_candidate(path):
                yield path


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def scrub(text: str) -> str:
    value = text.strip()
    value = re.sub(rf"(?i)({SECRET_NAME})(\s*[:=]\s*['\"]?)([^'\"\s]+)", r"\1\2<redacted>", value)
    value = re.sub(rf"(?i)(['\"]{SECRET_NAME}['\"]\s*:\s*['\"])([^'\"]+)(['\"])", r"\1<redacted>\3", value)
    value = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "AKIA<redacted>", value)
    value = re.sub(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b", "gh_<redacted>", value)
    value = re.sub(r"\bsk-[A-Za-z0-9_-]{20,}\b", "sk-<redacted>", value)
    value = re.sub(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "xox<redacted>", value)
    if len(value) > 180:
        value = value[:177] + "..."
    return value


def add_match(
    buckets: dict[str, list[Match]],
    category: str,
    root: Path,
    path: Path,
    line_no: int,
    line: str,
    max_matches: int,
) -> None:
    if len(buckets[category]) >= max_matches:
        return
    for label, pattern in PATTERNS[category]:
        if pattern.search(line):
            buckets[category].append(
                Match(
                    category=category,
                    label=label,
                    path=relative(path, root),
                    line=line_no,
                    preview=scrub(line),
                )
            )
            return


def collect(root: Path, max_bytes: int, max_matches: int) -> Inventory:
    buckets: dict[str, list[Match]] = {category: [] for category in PATTERNS}
    candidate_configs: set[str] = set()

    for path in iter_files(root, max_bytes):
        rel_path = relative(path, root)
        lower = rel_path.lower()
        if path.name in CONFIG_NAMES or path.name.startswith(".env") or any(
            token in lower for token in ("mcp", "plugin", "agent", "prompt", "retrieval", "memory", "workflow", "values", "config")
        ):
            candidate_configs.add(rel_path)

        try:
            lines = path.read_text(errors="ignore").splitlines()
        except OSError:
            continue

        for line_no, line in enumerate(lines, start=1):
            for category in PATTERNS:
                add_match(buckets, category, root, path, line_no, line, max_matches)

    return Inventory(
        root=str(root),
        model_calls=buckets["model_calls"],
        prompt_construction=buckets["prompt_construction"],
        tool_definitions=buckets["tool_definitions"],
        mcp_plugin_configs=buckets["mcp_plugin_configs"],
        retrieval_sources=buckets["retrieval_sources"],
        memory_stores=buckets["memory_stores"],
        file_network_code_tools=buckets["file_network_code_tools"],
        approval_gates=buckets["approval_gates"],
        output_sinks=buckets["output_sinks"],
        sensitive_data_signals=buckets["sensitive_data_signals"],
        candidate_config_files=sorted(candidate_configs),
    )


def render_matches(title: str, matches: list[Match]) -> list[str]:
    lines = [f"## {title}"]
    if not matches:
        lines.append("- None found by pattern scan.")
        return lines
    for match in matches:
        lines.append(f"- `{match.path}:{match.line}` [{match.label}] {match.preview}")
    return lines


def render_markdown(inventory: Inventory) -> str:
    sections: list[str] = [
        "# Agent Surface Inventory",
        "",
        f"Root: `{inventory.root}`",
        "",
        "This is a pattern-based, read-only inventory. Verify every safety claim against the code path.",
        "",
        "## Candidate Config Files",
    ]
    if inventory.candidate_config_files:
        sections.extend(f"- `{path}`" for path in inventory.candidate_config_files)
    else:
        sections.append("- None found by pattern scan.")
    section_map = [
        ("Model Calls", inventory.model_calls),
        ("Prompt Construction", inventory.prompt_construction),
        ("Tool Definitions", inventory.tool_definitions),
        ("MCP And Plugin Configs", inventory.mcp_plugin_configs),
        ("Retrieval Sources", inventory.retrieval_sources),
        ("Memory Stores", inventory.memory_stores),
        ("File, Network, Code, And Browser Tools", inventory.file_network_code_tools),
        ("Approval Gates", inventory.approval_gates),
        ("Output Sinks", inventory.output_sinks),
        ("Sensitive Data Signals", inventory.sensitive_data_signals),
    ]
    for title, matches in section_map:
        sections.append("")
        sections.extend(render_matches(title, matches))
    return "\n".join(sections) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to scan")
    parser.add_argument("--max-bytes", type=int, default=512_000, help="Skip files larger than this size")
    parser.add_argument("--max-matches", type=int, default=80, help="Maximum matches per category")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    inventory = collect(root, args.max_bytes, args.max_matches)
    if args.format == "json":
        print(json.dumps(asdict(inventory), indent=2, sort_keys=True))
    else:
        print(render_markdown(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
