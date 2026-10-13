# Contributing to sign-language-avatar-generator

Thanks for wanting to push the tater. This repo is a Windows-first desktop
tool that turns spoken or typed language into a rigged sign-language avatar
in real time. Contributions land through PRs against `main`.

## Dev setup

```
git clone https://github.com/sam/sign-language-avatar-generator
cd sign-language-avatar-generator
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_assets.py
python -m sla.main --config config/default.toml
```

## Layout

- `sla/handlers/` — thin, one job each. They validate input and call a service. No business logic lives here.
- `sla/services/` — the meat. Gloss planning, avatar synthesis, captioning, streaming.
- `sla/models/` — dataclasses and pydantic schemas shared across services.
- `sla/platform/` — Windows adapters (audio capture, TTS bridge, overlay window).
- `sla/utils/` — logging, timing, audio helper functions.

## Rules

- Handlers stay under 40 lines. If a handler grows, the logic belongs in a service.
- Every service is injectable — no module-level singletons, take deps in `__init__`.
- New behavior needs a test in `tests/`. We run `pytest -q` on every PR.
- Type hints mandatory on public functions. We enforce with `mypy sla`.
- Don't commit model weights. Put fetch logic in `scripts/`.

## Commit style

Conventional commits: `feat(services): add ISL gloss reordering`,
`fix(platform): guard win32com TTS when engine missing`.