"""Entry point: wire config -> services -> handler dispatch loop."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sla.config.loader import load_config
from sla.platform.win_audio import WindowsAudioCapture
from sla.services.avatar_service import AvatarService
from sla.services.caption_service import CaptionService
from sla.services.gloss_service import GlossService
from sla.services.render_service import RenderService
from sla.utils.logging import configure_logging, get_logger

log = get_logger(__name__)


def build_services(cfg):
    audio = WindowsAudioCapture(device=cfg.audio.device, samplerate=cfg.audio.samplerate)
    caption = CaptionService(model_dir=cfg.models.caption_dir, language=cfg.language.tag)
    gloss = GlossService(grammar_pack=cfg.models.gloss_pack, language=cfg.language.tag)
    render = RenderService(rig_pack=cfg.models.rig_pack, backend=cfg.render.backend)
    return AvatarService(audio=audio, caption=caption, gloss=gloss, render=render, cfg=cfg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sla")
    parser.add_argument("--config", type=Path, default=Path("config/default.toml"))
    parser.add_argument("--text", help="skip audio capture, synthesize from text")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    configure_logging(cfg.log_level)
    log.info("boot", version=cfg.version, language=cfg.language.tag)

    svc = build_services(cfg)
    if args.text:
        svc.run_text_once(args.text)
    else:
        svc.run_stream()
    return 0


if __name__ == "__main__":
    sys.exit(main())