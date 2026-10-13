"""End-to-end text -> frames pipeline with stub backend."""
from pathlib import Path

import numpy as np
import pytest

from sla.config.loader import AppConfig
from sla.platform.win_audio import WindowsAudioCapture
from sla.services.avatar_service import AvatarService
from sla.services.caption_service import CaptionService
from sla.services.gloss_service import GlossService
from sla.services.render_service import RenderService


@pytest.fixture
def service(tmp_path: Path) -> AvatarService:
    cfg = AppConfig()
    cfg.render.backend = "stub"
    cfg.render.overlay = False
    return AvatarService(
        audio=WindowsAudioCapture(),
        caption=CaptionService(model_dir=tmp_path / "cap", language="ase"),
        gloss=GlossService(grammar_pack=tmp_path / "missing.json", language="ase"),
        render=RenderService(rig_pack=tmp_path / "rig.glb", backend="stub", fps=30),
        cfg=cfg,
    )


def test_text_pipeline_emits_frames(service: AvatarService) -> None:
    result = service.process_text("hello potato")
    assert result.frames_emitted > 0
    assert result.backend == "stub"
    assert result.gloss.language == "ase"


def test_low_confidence_audio_drops(service: AvatarService) -> None:
    pcm = np.zeros(1600, dtype=np.float32)
    out = service.process_audio(pcm)
    assert out is None or out.segment.confidence >= 0.35