"""structlog-lite: JSON logs to stderr, human logs to console."""
from __future__ import annotations

import json
import logging
import sys
from typing import Any


class _JsonFmt(logging.Formatter):
    def format(self, rec: logging.LogRecord) -> str:
        payload = {"ts": self.formatTime(rec), "level": rec.levelname, "msg": rec.getMessage()}
        payload.update(getattr(rec, "extra_fields", {}))
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JsonFmt())
    root = logging.getLogger("sla")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), {})


def _adapt_extra(extra: dict[str, Any]) -> dict[str, Any]:
    return {"extra_fields": extra}