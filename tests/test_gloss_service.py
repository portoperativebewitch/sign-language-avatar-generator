"""Gloss reorder + drop-copula behavior across languages."""
from pathlib import Path

import pytest

from sla.models.schemas import CaptionSegment
from sla.services.gloss_service import GlossService


@pytest.fixture
def ase_service(tmp_path: Path) -> GlossService:
    return GlossService(grammar_pack=tmp_path / "missing.json", language="ase")


def test_drops_articles_and_copula(ase_service: GlossService) -> None:
    seg = CaptionSegment(text="the cat is sleeping", start_ms=0, end_ms=900, confidence=0.9)
    gloss = ase_service.to_gloss(seg)
    lemmas = [t.lemma for t in gloss.tokens]
    assert "the" not in lemmas
    assert "is" not in lemmas
    assert "sleeping" in lemmas


def test_isl_reorders_to_sov(tmp_path: Path) -> None:
    svc = GlossService(grammar_pack=tmp_path / "missing.json", language="isl")
    seg = CaptionSegment(text="i eat rice", start_ms=0, end_ms=600, confidence=0.9)
    gloss = svc.to_gloss(seg)
    pos = [t.pos for t in gloss.tokens]
    assert pos[-1] == "v", f"expected verb last for SOV, got {pos}"


def test_render_text_uppercases(ase_service: GlossService) -> None:
    seg = CaptionSegment(text="hello", start_ms=0, end_ms=300, confidence=1.0)
    gloss = ase_service.to_gloss(seg)
    assert gloss.render_text() == "HELLO"