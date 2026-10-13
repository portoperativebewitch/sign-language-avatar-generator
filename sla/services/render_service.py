"""Gloss -> AvatarFrame stream. Owns rig selection + native/onnx backend pick."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sla.models.schemas import AvatarFrame, GlossSequence
from sla.platform.render_bridge import RenderBridge
from sla.utils.logging import get_logger

log = get_logger(__name__)


class RenderService:
    def __init__(self, rig_pack: Path, backend: str = "onnx", fps: int = 30) -> None:
        self.rig_pack = rig_pack
        self.backend = backend
        self.fps = fps
        self._bridge = RenderBridge(backend=backend)

    def synthesize(self, gloss: GlossSequence, start_ms: int) -> Iterator[AvatarFrame]:
        """Yield frames at `fps`. Frame count = tokens * base_duration."""
        base_ms = int(1000 / self.fps)
        for i, token in enumerate(gloss.tokens):
            for f in range(6):  # ~200ms per token at 30fps
                ts = start_ms + i * 200 + f * base_ms
                pose = self._bridge.pose_for(token, frame=f)
                yield AvatarFrame(ts_ms=ts, pose_joints=pose, blendshapes={})

    def close(self) -> None:
        self._bridge.close()