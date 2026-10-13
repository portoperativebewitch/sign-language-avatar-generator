"""Natural language -> sign gloss. Rule-based reorder + lexicon lookup.

Real sign languages don't map 1:1 to spoken word order. ASL drops articles
and copulas; ISL/BSL reorder to SOV. This service owns that transform.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from sla.models.schemas import CaptionSegment, GlossSequence, GlossToken
from sla.utils.logging import get_logger

log = get_logger(__name__)

_DROP_POS = {"det", "aux", "cop"}
_FINGERSPELL_FALLBACK = True


class GlossService:
    def __init__(self, grammar_pack: Path, language: str = "ase") -> None:
        self.language = language
        self.grammar_pack = grammar_pack
        self._lexicon: dict[str, str] = {}
        self._nonmanual: dict[str, list[str]] = {}
        self._load()

    def _load(self) -> None:
        if self.grammar_pack.exists():
            data = json.loads(self.grammar_pack.read_text(encoding="utf-8"))
            self._lexicon = data.get("lexicon", {})
            self._nonmanual = data.get("nonmanual", {})
            log.info("gloss_pack_loaded", entries=len(self._lexicon))
        else:
            log.warning("gloss_pack_missing", path=str(self.grammar_pack))

    def to_gloss(self, segment: CaptionSegment) -> GlossSequence:
        words = re.findall(r"[A-Za-z']+", segment.text.lower())
        tokens: list[GlossToken] = []
        for w in words:
            if w in {"the", "a", "an", "is", "are", "was", "were"}:
                continue
            lemma = self._lexicon.get(w, w)
            fingerspell = w not in self._lexicon and _FINGERSPELL_FALLBACK and len(w) > 3
            tokens.append(
                GlossToken(
                    lemma=lemma,
                    pos=self._guess_pos(lemma),
                    fingerspell=fingerspell,
                    nonmanual=self._nonmanual.get(lemma, []),
                )
            )
        if self.language in {"isl", "bsl"}:
            tokens = self._to_sov(tokens)
        return GlossSequence(language=self.language, tokens=tokens)

    @staticmethod
    def _guess_pos(word: str) -> str:
        if word.endswith("ly"):
            return "adv"
        if word.endswith("ing") or word.endswith("ed"):
            return "v"
        return "n"

    @staticmethod
    def _to_sov(tokens: list[GlossToken]) -> list[GlossToken]:
        verbs = [t for t in tokens if t.pos == "v"]
        rest = [t for t in tokens if t.pos != "v"]
        return rest + verbs