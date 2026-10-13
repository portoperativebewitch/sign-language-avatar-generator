"""Push AvatarFrames to the Win32 overlay window (tkinter stub for dev)."""
from __future__ import annotations

from sla.models.schemas import AvatarFrame
from sla.utils.logging import get_logger

log = get_logger(__name__)


class OverlaySink:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._count = 0

    def push(self, frame: AvatarFrame) -> None:
        if not self.enabled:
            return
        self._count += 1
        if self._count % 30 == 0:
            log.debug("overlay_frame", ts=frame.ts_ms, joints=len(frame.pose_joints))

    def close(self) -> None:
        log.info("overlay_closed", frames=self._count)