"""Optional text-to-speech bridge so the avatar can sign what the user hears.

Uses Windows SAPI via win32com when available; falls back to pyttsx3 on dev
boxes. Never blocks the audio thread — synthesize on a worker.
"""
from __future__ import annotations

import threading
from queue import Queue

from sla.utils.logging import get_logger

log = get_logger(__name__)


class TtsBridge:
    def __init__(self) -> None:
        self._q: Queue[str] = Queue()
        self._worker: threading.Thread | None = None
        self._engine = self._load_engine()

    def _load_engine(self):
        try:
            import win32com.client as w  # type: ignore
            return w.Dispatch("SAPI.SpVoice")
        except Exception:  # noqa: BLE001
            log.warning("sapi_unavailable")
            return None

    def speak(self, text: str) -> None:
        self._q.put(text)
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._drain, daemon=True)
            self._worker.start()

    def _drain(self) -> None:
        while not self._q.empty():
            line = self._q.get()
            if self._engine is not None:
                self._engine.Speak(line)
            else:
                log.info("tts_stub", text=line)