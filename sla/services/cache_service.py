"""Disk cache for gloss packs and rendered frame strips. LRU, 512MB cap.

*Uses JSON, not pickle — untrusted rig packs must never deserialize pickle.
That's the whole reason this file exists.*
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from sla.utils.logging import get_logger

log = get_logger(__name__)

DEFAULT_ROOT = Path.home() / ".sla_cache"
MAX_BYTES = 512 * 1024 * 1024


class CacheService:
    def __init__(self, root: Path = DEFAULT_ROOT, max_bytes: int = MAX_BYTES) -> None:
        self.root = root
        self.max_bytes = max_bytes
        self.root.mkdir(parents=True, exist_ok=True)

    def _key_path(self, namespace: str, raw_key: str) -> Path:
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
        return self.root / namespace / f"{digest}.json"

    def get(self, namespace: str, key: str) -> dict | None:
        p = self._key_path(namespace, key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf