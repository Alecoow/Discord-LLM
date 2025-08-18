from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, TypedDict

class ChatMessage(TypedDict):
    role: str
    content: str

# convert OpenAI response content into a regular string
def normalize_content(content: Any) -> str:
    if isinstance(content, list):
        return "".join(
            p.get("text", "")
            for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        )
    if content is None:
        return ""
    return str(content)

# Remove invalid/empty messages and normalize roles
def sanitize_messages(messages: Optional[Iterable[Dict[str, Any]]]) -> List[ChatMessage]:
    clean: List[ChatMessage] = []
    for m in messages or []:
        role = m.get("role")
        if role not in ("system", "user", "assistant"):
            continue
        text = normalize_content(m.get("content")).strip()
        if text:
            clean.append({"role": role, "content": text})
    return clean

# remove thinking tokens
def strip_think(text: str, marker: str) -> str:
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    return text.split(marker, 1)[1].strip() if marker in text else text.strip()

# Ensure message complies with Discord's 2000 character limit
def truncate_response(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = limit - len("\n\n[RESPONSE TRUNCATED]")
    return text[:max(0, head)].rstrip() + "\n\n[RESPONSE TRUNCATED]"