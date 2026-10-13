"""Orchestrator. Audio/caption -> gloss -> frames -> sink. The only fat service."""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from sla.config.loader import AppConfig
from sla.models.schemas import PipelineResult
from sla.platform.win_audio import WindowsAudioCapture
from sla.services.caption_service import CaptionService
from sla.services.gloss_service import GlossService
from sla.services.render_service import RenderService
from sla.platform.overlay_sink import OverlaySink
from sla.utils.logging import get_logger
from sla.utils.timing import Stopwatch

log = get_logger(__name__)


class AvatarService:
    def __init__(
        self,
        audio: WindowsAudioCapture,
        caption: CaptionService,
        gloss: GlossService,
        render: RenderService,
        cfg: AppConfig,
    ) -> None:
        self.audio = audio
        self.caption = caption
        self.gloss = gloss
        self.render = render
        self.cfg = cfg
        self.sink = OverlaySink(enabled=cfg.render.overlay)

    def process_text(self, text: str) -> PipelineResult:
        from sla.models.schemas import CaptionSegment
        seg = CaptionSegment(text=text, start_ms=0, end_ms=len(text) * 60, confidence=1.0)
        return self._run(seg)

    def process_audio(self, pcm: np.ndarray) -> PipelineResult | None:
        seg = self.caption.transcribe(pcm, ts_ms=self._now_ms())
        if seg.confidence < 0.35:
            return None
        return self._run(seg)

    def _run(self, seg) -> PipelineResult:
        with Stopwatch() as sw:
            gloss = self.gloss.to_gloss(seg)
            n = 0
            for frame in self.render.synthesize(gloss, start_ms=seg.start_ms):
                self.sink.push(frame)
                n += 1
        log.info("pipeline_run", gloss=len(gloss.tokens), frames=n, ms=sw.elapsed_ms)
        return PipelineResult(segment=seg, gloss=gloss, frames_emitted=n, backend=self.render.backend)

    def run_text_once(self, text: str) -> None:
        self.process_text(text)

    def run_stream(self) -> None:
        for chunk in self.audio.stream(self.cfg.audio.chunk_ms):
            self.process_audio(chunk)

    @staticmethod
    def _now_ms() -> int:
        import time
        return int(time.time() * 1000)