"""Thin handler: raw pcm chunk -> PipelineResult. No business logic here."""
from __future__ import annotations

import numpy as np

from sla.models.schemas import PipelineResult
from sla.services.avatar_service import AvatarService


def handle_audio_chunk(svc: AvatarService, pcm: np.ndarray) -> PipelineResult | None:
    if pcm.size == 0:
        return None
    return svc.process_audio(pcm)