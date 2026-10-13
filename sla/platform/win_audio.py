"""Windows audio capture adapter via sounddevice (WASAPI shared mode)."""
from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import sounddevice as sd

from sla.utils.logging import get_logger

log = get_logger(__name__)


class WindowsAudioCapture:
    def __init__(self, device: str | None = None, samplerate: int = 16_000) -> None:
        self.device = device
        self.samplerate = samplerate

    def stream(self, chunk_ms: int = 20) -> Iterator[np.ndarray]:
        blocksize = int(self.samplerate * chunk_ms / 1000)
        with sd.InputStream(
            device=self.device,
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            blocksize=blocksize,
        ) as s:
            log.info("audio_stream_open", device=self.device, sr=self.samplerate)
            while True:
                data, _ = s.read(blocksize)
                yield data[:, 0]