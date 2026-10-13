"""Tiny context manager stopwatch used by services for p99 tracking."""
from __future__ import annotations

import time


class Stopwatch:
    __slots__ = ("_t0", "elapsed_ms")

    def __init__(self) -> None:
        self._t0 = 0.0
        self.elapsed_ms = 0.0

    def __enter__(self) -> "Stopwatch":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed_ms = round((time.perf_counter() - self._t0) * 1000, 2)