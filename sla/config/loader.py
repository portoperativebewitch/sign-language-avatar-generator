"""TOML config loader with pydantic validation and sane Windows defaults."""
from __future__ import annotations

from pathlib import Path

import tomllib
from pydantic import BaseModel, Field


class AudioCfg(BaseModel):
    device: str | None = None
    samplerate: int = 16_000
    chunk_ms: int = 20


class ModelsCfg(BaseModel):
    caption_dir: Path = Path("models/checkpoints/caption")
    gloss_pack: Path = Path("models/checkpoints/gloss_lexicon.json")
    rig_pack: Path = Path("assets/rigs/default_rig.glb")


class RenderCfg(BaseModel):
    backend: str = "onnx"          # "onnx" | "native" | "stub"
    fps: int = 30
    overlay: bool = True


class LanguageCfg(BaseModel):
    tag: str = "ase"               # ase=American, bsl=British, isl=Indian
    gloss_order: str = "sov"


class AppConfig(BaseModel):
    version: str = "0.4.1"
    log_level: str = "INFO"
    audio: AudioCfg = Field(default_factory=AudioCfg)
    models: ModelsCfg = Field(default_factory=ModelsCfg)
    render: RenderCfg = Field(default_factory=RenderCfg)
    language: LanguageCfg = Field(default_factory=LanguageCfg)


def load_config(path: Path) -> AppConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return AppConfig.model_validate(raw)