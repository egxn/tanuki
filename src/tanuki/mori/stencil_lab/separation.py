"""separation.py
────────────────
Colour separation for the Stencil Lab.

A *separation* splits an image into one or more **ink-coverage planes**: a
grayscale array in [0, 1] where ``1.0`` means "lay down full ink here".  This is
exactly what a pattern generator wants — more coverage → bigger halftone dots,
thicker lines, denser hatching.

Each plane is tagged with a preview ``color`` (RGB 0–255) so the result can be
composited or exported per channel.

Returned value
──────────────
Every function returns a :class:`Separation`: an ordered list of
``(name, plane, color)`` channels.  Order is print order (e.g. C, M, Y, K).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .image_io import to_grayscale

Color = tuple[int, int, int]


@dataclass(slots=True)
class Channel:
    name: str
    plane: np.ndarray  # ink coverage in [0, 1], shape (H, W)
    color: Color


@dataclass(slots=True)
class Separation:
    channels: list[Channel]

    def __iter__(self):
        return iter(self.channels)

    def __len__(self) -> int:
        return len(self.channels)

    def __getitem__(self, key: int | str) -> Channel:
        if isinstance(key, int):
            return self.channels[key]
        for ch in self.channels:
            if ch.name == key:
                return ch
        raise KeyError(key)

    @property
    def names(self) -> list[str]:
        return [ch.name for ch in self.channels]


def _clip(a: np.ndarray) -> np.ndarray:
    return np.clip(a, 0.0, 1.0)


def grayscale(arr: np.ndarray) -> Separation:
    """Single black ink plane (coverage = darkness)."""
    cov = 1.0 - to_grayscale(arr)
    return Separation([Channel("key", cov, (0, 0, 0))])


def rgb(arr: np.ndarray) -> Separation:
    """Split into additive Red / Green / Blue ink planes.

    Coverage is the channel intensity, so a bright-red region produces heavy
    red-ink coverage — suited to additive (light-on-dark) previews.
    """
    if arr.ndim != 3:
        raise ValueError("rgb() needs a colour image")
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    return Separation([
        Channel("red", _clip(r), (255, 0, 0)),
        Channel("green", _clip(g), (0, 255, 0)),
        Channel("blue", _clip(b), (0, 0, 255)),
    ])


def cmyk(arr: np.ndarray) -> Separation:
    """Standard CMYK separation with GCR-style black generation.

    Uses the textbook un-calibrated conversion::

        K = 1 - max(R, G, B)
        C = (1 - R - K) / (1 - K)
        M = (1 - G - K) / (1 - K)
        Y = (1 - B - K) / (1 - K)
    """
    if arr.ndim != 3:
        raise ValueError("cmyk() needs a colour image")
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    k = 1.0 - np.maximum.reduce([r, g, b])
    denom = np.where(k < 1.0, 1.0 - k, 1.0)  # avoid /0 where K == 1
    c = np.where(k < 1.0, (1.0 - r - k) / denom, 0.0)
    m = np.where(k < 1.0, (1.0 - g - k) / denom, 0.0)
    y = np.where(k < 1.0, (1.0 - b - k) / denom, 0.0)
    return Separation([
        Channel("cyan", _clip(c), (0, 174, 239)),
        Channel("magenta", _clip(m), (236, 0, 140)),
        Channel("yellow", _clip(y), (255, 242, 0)),
        Channel("key", _clip(k), (35, 31, 32)),
    ])


def duotone(arr: np.ndarray, shadow: Color = (20, 20, 90),
            base: Color = (230, 80, 60)) -> Separation:
    """Two-ink build from luminance.

    ``base`` ink carries the whole tonal range; ``shadow`` ink adds extra
    density in the darks — the classic risograph two-colour look.
    """
    tone = to_grayscale(arr)
    base_cov = 1.0 - tone
    shadow_cov = _clip(1.0 - 2.0 * tone)
    return Separation([
        Channel("base", _clip(base_cov), base),
        Channel("shadow", shadow_cov, shadow),
    ])


def tritone(arr: np.ndarray, shadow: Color = (20, 20, 60),
            mid: Color = (220, 90, 70), highlight: Color = (240, 210, 120)) -> Separation:
    """Three-ink build: shadow / midtone / highlight ink planes."""
    tone = to_grayscale(arr)
    shadow_cov = _clip(1.0 - 2.0 * tone)
    mid_cov = 1.0 - np.abs(2.0 * tone - 1.0)        # peaks at mid-grey
    highlight_cov = _clip(2.0 * tone - 1.0)
    return Separation([
        Channel("shadow", shadow_cov, shadow),
        Channel("mid", _clip(mid_cov), mid),
        Channel("highlight", highlight_cov, highlight),
    ])
