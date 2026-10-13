"""Download rig + ONNX checkpoints from the release mirror. Idempotent."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import httpx

BASE = "https://mirror.sign-language-avatar-generator.dev/v0.4"
FILES = {
    "models/checkpoints/caption/caption_int8.onnx": "sha256:...",
    "models/checkpoints/gloss_lexicon.json": "sha256:...",
    "assets/rigs/default_rig.glb": "sha256:...",
}


def fetch_one(rel: str, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[skip] {rel}")
        return
    with httpx.stream("GET", url, timeout=60.0) as r:
        r.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in r.iter_bytes(1 << 16):
                fh.write(chunk)
    print(f"[ok]   {rel}")


def main() -> int:
    root = Path.cwd()
    for rel in FILES:
        fetch_one(rel, f"{BASE}/{rel}", root / rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())