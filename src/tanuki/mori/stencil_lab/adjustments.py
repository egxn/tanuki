"""adjustments.py
────────────────
Pointwise and spatial image adjustments for the Stencil Lab.

All functions take and return float64 arrays in [0, 1] (grayscale ``(H, W)`` or
colour ``(H, W, C)``) and never mutate their input.  Pointwise operations work
on any shape; spatial ones (blur / sharpen / edges) operate per channel.

These are the knobs a user reaches for *before* a pattern is generated — to
shape contrast, crush midtones to pure black/white, or pull edges out of a
photo for a line-art look.
"""

from __future__ import annotations

import numpy as np


def _clip(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0.0, 1.0)


# ─── Pointwise tone adjustments ────────────────────────────────────────────────

def brightness(arr: np.ndarray, amount: float) -> np.ndarray:
    """Add ``amount`` (−1..1) to every pixel."""
    return _clip(arr + amount)


def contrast(arr: np.ndarray, amount: float) -> np.ndarray:
    """Scale contrast about mid-grey. ``amount`` 1.0 = unchanged, >1 stronger."""
    return _clip((arr - 0.5) * amount + 0.5)


def gamma(arr: np.ndarray, g: float) -> np.ndarray:
    """Gamma correction. ``g`` < 1 brightens, > 1 darkens."""
    if g <= 0:
        raise ValueError("gamma must be > 0")
    return _clip(np.power(_clip(arr), g))


def invert(arr: np.ndarray) -> np.ndarray:
    """Photographic negative (alpha channel, if present, is preserved)."""
    if arr.ndim == 3 and arr.shape[-1] == 4:
        out = arr.copy()
        out[..., :3] = 1.0 - out[..., :3]
        return out
    return 1.0 - arr


def threshold(arr: np.ndarray, level: float = 0.5) -> np.ndarray:
    """Binarise: pixels below ``level`` → 0, at/above → 1."""
    return (arr >= level).astype(np.float64)


def posterize(arr: np.ndarray, levels: int = 4) -> np.ndarray:
    """Quantise tones into ``levels`` discrete steps."""
    if levels < 2:
        raise ValueError("levels must be >= 2")
    q = np.round(_clip(arr) * (levels - 1)) / (levels - 1)
    return q


# ─── Spatial filters ───────────────────────────────────────────────────────────

def _gaussian_kernel(radius: int) -> np.ndarray:
    sigma = max(radius / 2.0, 1e-3)
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-(x * x) / (2.0 * sigma * sigma))
    return k / k.sum()


def _convolve_1d(arr: np.ndarray, kernel: np.ndarray, axis: int) -> np.ndarray:
    """Separable 1-D convolution with edge padding, along ``axis`` of a 2-D array."""
    pad = len(kernel) // 2
    work = np.moveaxis(arr, axis, -1)
    padded = np.pad(work, [(0, 0)] * (work.ndim - 1) + [(pad, pad)], mode="edge")
    # Sliding-window dot product.
    windows = np.lib.stride_tricks.sliding_window_view(padded, len(kernel), axis=-1)
    out = windows @ kernel
    return np.moveaxis(out, -1, axis)


def _spatial(arr: np.ndarray, fn) -> np.ndarray:
    """Apply a 2-D spatial filter ``fn`` per channel."""
    if arr.ndim == 2:
        return fn(arr)
    channels = [fn(arr[..., c]) for c in range(arr.shape[-1])]
    return np.stack(channels, axis=-1)


def blur(arr: np.ndarray, radius: int = 2) -> np.ndarray:
    """Separable Gaussian blur with the given pixel ``radius``."""
    if radius < 1:
        return arr.copy()
    kernel = _gaussian_kernel(radius)

    def fn(plane: np.ndarray) -> np.ndarray:
        return _convolve_1d(_convolve_1d(plane, kernel, 0), kernel, 1)

    return _clip(_spatial(arr, fn))


def sharpen(arr: np.ndarray, amount: float = 1.0, radius: int = 2) -> np.ndarray:
    """Unsharp mask: ``arr + amount * (arr - blur(arr))``."""
    blurred = blur(arr, radius)
    return _clip(arr + amount * (arr - blurred))


def edges(arr: np.ndarray) -> np.ndarray:
    """Sobel edge magnitude, normalised to [0, 1] (bright = strong edge)."""
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = kx.T

    def fn(plane: np.ndarray) -> np.ndarray:
        padded = np.pad(plane, 1, mode="edge")
        win = np.lib.stride_tricks.sliding_window_view(padded, (3, 3))
        gx = np.einsum("ijkl,kl->ij", win, kx)
        gy = np.einsum("ijkl,kl->ij", win, ky)
        return np.hypot(gx, gy)

    mag = _spatial(arr, fn)
    peak = mag.max()
    return mag / peak if peak > 0 else mag
