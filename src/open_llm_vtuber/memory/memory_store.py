import json
import os
import re
import sqlite3
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal

from loguru import logger


MemoryBackend = Literal["json", "sqlite"]


class MemoryStore:
    """Small local long-term memory store for cross-session recall."""

    def __init__(
        self,
        conf_uid: str,
        backend: MemoryBackend = "json",
        max_items: int = 80,
        base_dir: str | Path = "cache/long_term_memory",
    ):
        self.conf_uid = self._safe_component(conf_uid or "default")
        self.backend: MemoryBackend = backend if backend in ("json", "sqlite") else "json"
        self.max_items = max(1, int(max_items or 80))
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / f"{self.conf_uid}.{self.backend}"

        if self.backend == "sqlite":
            self._init_sqlite()
        else:
            self._init_json()

    @staticmethod
    def _safe_component(value: str) -> str:
        cleaned = os.path.basename(str(value).strip())
        return re.sub(r"[^\w\- ]+", "_", cleaned)[:120] or "default"

    def _init_json(self) -> None:
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def search(self, query: str, limit: int = 6) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        memories = self.list_memories()
        if not query_tokens:
            return memories[-limit:]

        scored = []
        query_counter = Counter(query_tokens)
        for item in memories:
            item_tokens = self._tokenize(
                f"{item.get('content', '')} {' '.join(item.get('keywords', []))}"
            )
            if not item_tokens:
                continue
            score = sum((Counter(item_tokens) & query_counter).values())
            if score:
                scored.append((score, item))

        scored.sort(
            key=lambda pair: (
                pair[0],
                pair[1].get("updated_at", pair[1].get("created_at", "")),
            ),
            reverse=True,
        )
        return [item for _, item in scored[:limit]]

    def remember_turn(
        self,
        user_text: str,
        assistant_text: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        user_text = (user_text or "").strip()
        assistant_text = (assistant_text or "").strip()
        if not user_text and not assistant_text:
            return

        content = self._summarize_turn(user_text, assistant_text)
        if not content:
            return

        kind = "fact" if self._looks_like_fact(user_text) else "turn_summary"
        self.add_memory(kind=kind, content=content, metadata=metadata or {})

    def add_memory(
        self,
        kind: str,
        content: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        content = content.strip()
        if not content:
            return

        now = datetime.now().isoformat(timespec="seconds")
        item = {
            "id": uuid.uuid4().hex,
            "kind": kind,
            "content": content,
            "keywords": sorted(set(self._tokenize(content)))[:24],
            "created_at": now,
            "updated_at": now,
            "metadata": metadata or {},
        }

        if self.backend == "sqlite":
            self._add_sqlite(item)
        else:
            self._add_json(item)
        self.prune()

    def list_memories(self) -> List[Dict[str, Any]]:
        if self.backend == "sqlite":
            return self._list_sqlite()
        return self._list_json()

    def clear(self) -> None:
        if self.backend == "sqlite":
            with sqlite3.connect(self.path) as conn:
                conn.execute("DELETE FROM memories")
                conn.commit()
            return
        self.path.write_text("[]", encoding="utf-8")

    def prune(self) -> None:
        memories = self.list_memories()
        overflow = len(memories) - self.max_items
        if overflow <= 0:
            return

        keep = memories[overflow:]
        if self.backend == "sqlite":
            with sqlite3.connect(self.path) as conn:
                conn.execute("DELETE FROM memories")
                conn.executemany(
                    """
                    INSERT INTO memories
                    (id, kind, content, keywords, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [self._sqlite_tuple(item) for item in keep],
                )
                conn.commit()
            return

        self.path.write_text(json.dumps(keep, ensure_ascii=False, indent=2), encoding="utf-8")

    def _add_json(self, item: Dict[str, Any]) -> None:
        memories = self._list_json()
        memories.append(item)
        self.path.write_text(json.dumps(memories, ensure_ascii=False, indent=2), encoding="utf-8")

    def _list_json(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to read long-term memory JSON: {e}")
            return []

    def _add_sqlite(self, item: Dict[str, Any]) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                INSERT INTO memories
                (id, kind, content, keywords, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                self._sqlite_tuple(item),
            )
            conn.commit()

    def _list_sqlite(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                """
                SELECT id, kind, content, keywords, created_at, updated_at, metadata
                FROM memories ORDER BY created_at ASC
                """
            ).fetchall()

        return [
            {
                "id": row[0],
                "kind": row[1],
                "content": row[2],
                "keywords": json.loads(row[3]),
                "created_at": row[4],
                "updated_at": row[5],
                "metadata": json.loads(row[6]),
            }
            for row in rows
        ]

    def _sqlite_tuple(self, item: Dict[str, Any]) -> tuple:
        return (
            item["id"],
            item["kind"],
            item["content"],
            json.dumps(item["keywords"], ensure_ascii=False),
            item["created_at"],
            item["updated_at"],
            json.dumps(item["metadata"], ensure_ascii=False),
        )

    def _summarize_turn(self, user_text: str, assistant_text: str) -> str:
        if self._looks_like_fact(user_text):
            return f"使用者提到：{self._truncate(user_text, 240)}"

        user_part = self._truncate(user_text, 160)
        assistant_part = self._truncate(assistant_text, 160)
        if user_part and assistant_part:
            return f"使用者問：{user_part} / AI 回覆：{assistant_part}"
        return user_part or assistant_part

    def _looks_like_fact(self, text: str) -> bool:
        patterns = [
            r"記住",
            r"remember",
            r"my name is",
            r"我的名字",
            r"我叫",
            r"我是",
            r"我喜歡",
            r"我不喜歡",
            r"我的.*是",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in text and patterns)

    def _tokenize(self, text: str) -> List[str]:
        lowered = text.lower()
        latin_tokens = re.findall(r"[a-z0-9_]{2,}", lowered)
        cjk_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", lowered)
        cjk_bigrams = []
        for token in cjk_tokens:
            cjk_bigrams.extend(token[i : i + 2] for i in range(max(0, len(token) - 1)))
        return latin_tokens + cjk_tokens + cjk_bigrams

    def _truncate(self, text: str, max_length: int) -> str:
        text = re.sub(r"\s+", " ", text or "").strip()
        if len(text) <= max_length:
            return text
        return text[: max_length - 1] + "…"
