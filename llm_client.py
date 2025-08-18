from __future__ import annotations
import json
from typing import Any, Dict, Optional
import aiohttp
from settings import LLM_CHAT_URL, LLM_MODELS_URL, LLM_HEADERS

class LLMClient:
    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    # Initialize session
    async def start(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90))

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def list_models(self) -> Any:
        assert self._session, "LLM session not started"
        async with self._session.get(LLM_MODELS_URL, headers=LLM_HEADERS) as r:
            r.raise_for_status()
            return await r.json()

    async def chat(self, payload: Dict[str, Any]) -> Optional[str]:
        assert self._session, "LLM session not started"
        try:
            async with self._session.post(LLM_CHAT_URL, headers=LLM_HEADERS, json=payload) as r:
                text = await r.text()
                r.raise_for_status()
        except aiohttp.ClientError as e:
            print(f"[LLM] Request failed: {e}")
            return None

        try:
            data = json.loads(text)
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM] Bad JSON: {e}")
            print(text[:1000])
            return None