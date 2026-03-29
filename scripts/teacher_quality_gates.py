from __future__ import annotations

import re
from typing import Any


ELLIPSIS_RE = re.compile(r"…|â€¦|\.\.\.")
MARKDOWN_TABLE_RE = re.compile(r"\|\s*---|\|\s*Beschreibung\s*\|")
NOTE_TOKEN_RE = re.compile(r"\*\*(Hinweis|Achtung|Wichtig):\*\*", re.IGNORECASE)
MISUSED_SHORTCUT_RE = re.compile(r"Verwenden Sie dazu \*\*[^*]+:\*\*\.", re.IGNORECASE)


def _candidate_text(row: dict[str, Any]) -> str:
    candidate = row.get("candidate") or {}
    if row.get("record_type") == "sft_sample":
        messages = candidate.get("messages") or []
        for message in reversed(messages):
            if message.get("role") == "assistant":
                return str(message.get("content") or "")
        return ""
    return str(candidate.get("reference_answer") or "")


def blocking_artifact_reasons(row: dict[str, Any]) -> list[str]:
    text = _candidate_text(row)
    reasons: list[str] = []
    if not text.strip():
        reasons.append("missing candidate text")
        return reasons
    if ELLIPSIS_RE.search(text):
        reasons.append("contains ellipsis/truncation artifact")
    if MARKDOWN_TABLE_RE.search(text):
        reasons.append("contains markdown table artifact")
    if NOTE_TOKEN_RE.search(text):
        reasons.append("contains note label promoted as content")
    if MISUSED_SHORTCUT_RE.search(text):
        reasons.append("contains note label misused as shortcut")
    return reasons
