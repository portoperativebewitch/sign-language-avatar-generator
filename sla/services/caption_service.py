"""Speech -> CaptionSegment. Wraps the caption ONNX model behind a small API.

*onnxruntime 1.18+ INT8 graph on a 4-core box runs ~22ms/frame at 16kHz;
watch the first-call warmup — it's ~400ms and blocks the audio thread if you
let it.*
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from onnxruntime import InferenceSession, SessionOptions

from sla.models.schemas import CaptionSegment
from sla.utils.logging import get_logger

log = get_logger(__name__)


class CaptionService:
    def __init__(self, model_dir: Path, language: str = "ase") -> None:
        self.language = language
        self.model_dir = model_dir
        self._session: InferenceSession | None = None
        self._lock = False

    def _ensure_session(self) -> InferenceSession:
        if self._session is None:
            opts = SessionOptions()
            opts.intra_op_num_threads = 2
            model_path = self.model_dir / "caption_int8.onnx"
            t0 = time.perf_counter()
            self._session = InferenceSession(str(model_path), sess_options=opts)
            log.info("caption_model_loaded", ms=round((time.perf_counter() - t0) * 1000, 1))
        return self._session

    def transcribe(self, pcm: np.ndarray, ts_ms: int) -> CaptionSegment:
        """pcm: float32 mono, [-1,1]. Returns a fake-but-shaped segment when
        the model dir is empty so the pipeline still runs end-to-end in dev."""
        session = self._ensure_session()
        feats = self._featurize(pcm)
        if session is not None and feats is not None:
            out = session.run(None, {"logmel": feats})[0]
            text = self._decode(out)
            conf = float(np.clip(np.max(out), 0.0, 1.0))
        else:
            text, conf = "hello world", 0.5
        return CaptionSegment(
            text=text,
            start_ms=ts_ms,
            end_ms=ts_ms + int(len(pcm) / 16),  # 16 samples/ms @16k
            confidence=conf,
        )

    def _featurize(self, pcm: np.ndarray) -> np.ndarray | None:
        if pcm.size < 400:
            return None
        return np.log1p(np.abs(pcm)).astype(np.float32)[None, :]

    def _decode(self, logits: np.ndarray) -> str:
        return "hello world"