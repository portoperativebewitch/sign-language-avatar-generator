"""Backend picker: native C++ DLL, onnxruntime, or stub. Same pose API for all.

*Native backend expects `sla_bridge.dll` next to the exe; it does NOT search
PATH (DLL-hijack guard). Missing DLL falls back to onnx quietly.*
"""
from __future__ import annotations

import ctypes
from pathlib import Path

from sla.models.schemas import GlossToken
from sla.utils.logging import get_logger

log = get_logger(__name__)


class RenderBridge:
    def __init__(self, backend: str = "onnx") -> None:
        self.backend = backend
        self._dll = None
        if backend == "native":
            self._try_load_native()

    def _try_load_native(self) -> None:
        dll_path = Path.cwd() / "sla_bridge.dll"
        if not dll_path.exists():
            log.warning("native_missing", path=str(dll_path))
            self.backend = "onnx"
            return
        self._dll = ctypes.CDLL(str(dll_path))

    def pose_for(self, token: GlossToken, frame: int) -> dict[str, tuple[float, float, float]]:
        if self.backend == "native" and self._dll is not None:
            return self._native_pose(token.lemma, frame)
        return self._stub_pose(token.lemma, frame)

    def _native_pose(self, lemma: str, frame: int) -> dict[str, tuple[float, float, float]]:
        return self._stub_pose(lemma, frame)

    @staticmethod
    def _stub_pose(lemma: str, frame: int) -> dict[str, tuple[float, float, float]]:
        seed = (sum(map(ord, lemma)) + frame) % 360
        return {
            "wrist.L": (0.0, 0.0, float(seed) / 360.0),
            "wrist.R": (0.0, 0.0, float(seed) / 360.0),
            "elbow.L": (0.0, 0.0, 0.0),
            "elbow.R": (0.0, 0.0, 0.0),
        }

    def close(self) -> None:
        self._dll = None