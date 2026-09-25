"""Canonical series definitions for the Fiscalore channel.

Three original fictional hosts, one per visual series. Everything that varies
between series lives here: personality, visual style key, palette, TTS voices
and channel sign-off. Scenes, scripts and metadata all reference a series by id.

Adding a series means adding one entry to SERIES and extending the renderer
template map in renderer.py — no other module needs to change.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

ROTATION = ("arjun", "mira", "kabir")


@dataclass(frozen=True)
class Series:
    id: str
    host: str
    show: str
    persona: str
    style: str
    background: str
    surface: str
    ink: str
    accent: str
    muted: str
    signoff: str
    description: str

    @property
    def channel_suffix(self) -> str:
        return f" | {self.show} by {self.host}"


SERIES: Dict[str, Series] = {
    "arjun": Series(
        id="arjun",
        host="Arjun",
        show="The Quiet Ledger",
        persona="calm contrarian; dry, precise, never hype",
        style="educational",
        background="#F4EFE3",
        surface="#FFFDF7",
        ink="#17241F",
        accent="#1F7A5C",
        muted="#6B7A72",
        signoff="Arjun — The Quiet Ledger",
        description=(
            "Clean educational explainers: one financial idea per sentence, "
            "diagram-led, ledger-quiet pacing."
        ),
    ),
    "mira": Series(
        id="mira",
        host="Mira",
        show="Myth Busters",
        persona="myth buster; playful, surgical, enjoys the reveal",
        style="metaphor",
        background="#F3F1EE",
        surface="#FBFAF8",
        ink="#211E1B",
        accent="#E4572E",
        muted="#8A8078",
        signoff="Mira — Myth Busters",
        description=(
            "Minimal metaphors: almost-empty frames, one object doing the "
            "talking, hard visual reveals."
        ),
    ),
    "kabir": Series(
        id="kabir",
        host="Kabir",
        show="The Wealth Lab",
        persona="wealth-lab storyteller; cinematic, patient, cinematic beats",
        style="cinematic",
        background="#0C141D",
        surface="#152230",
        ink="#F2EDE4",
        accent="#E5B24A",
        muted="#7E8B99",
        signoff="Kabir — The Wealth Lab",
        description=(
            "Cinematic story scenes: recurring characters, depth layers, warm "
            "key light, slow camera moves."
        ),
    ),
}


def get(series_id: Optional[str]) -> Series:
    """Return a series by id, falling back to the first rotation entry."""
    if series_id and series_id in SERIES:
        return SERIES[series_id]
    return SERIES[ROTATION[0]]


def all_series() -> List[str]:
    return list(ROTATION)


def next_in_rotation(series_id: Optional[str]) -> str:
    """Next series id in round-robin order (wraps)."""
    if series_id not in SERIES:
        return ROTATION[0]
    idx = ROTATION.index(series_id)
    return ROTATION[(idx + 1) % len(ROTATION)]
