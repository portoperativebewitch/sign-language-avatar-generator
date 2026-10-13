"""Shared dataclasses / pydantic models crossing service boundaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


class CaptionSegment(BaseModel):
    text: str
    start_ms: int
    end_ms: int
    confidence: float = Field(ge=0.0, le=1.0)

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


class GlossToken(BaseModel):
    lemma: str
    pos: Literal["n", "v", "adj", "adv", "fn", "punct"]
    fingerspell: bool = False
    nonmanual: list[str] = Field(default_factory=list)  # e.g. ["brow_raise"]


class GlossSequence(BaseModel):
    language: str
    tokens: list[GlossToken] = Field(default_factory=list)

    def render_text(self) -> str:
        return " ".join(t.lemma.upper() for t in self.tokens)


@dataclass(slots=True)
class AvatarFrame:
    ts_ms: int
    pose_joints: dict[str, tuple[float, float, float]]
    blendshapes: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineResult:
    segment: CaptionSegment
    gloss: GlossSequence
    frames_emitted: int
    backend: str