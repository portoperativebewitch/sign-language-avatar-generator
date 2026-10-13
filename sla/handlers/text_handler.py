"""Thin handler: text in -> PipelineResult out. Delegates to AvatarService."""
from __future__ import annotations

from sla.models.schemas import PipelineResult
from sla.services.avatar_service import AvatarService


def handle_text(svc: AvatarService, text: str) -> PipelineResult:
    if not text.strip():
        raise ValueError("empty caption text")
    return svc.process_text(text)