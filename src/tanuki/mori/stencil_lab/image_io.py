"""image_io.py
────────────
Image loading / saving for the Stencil Lab.

Everything downstream works on **float64 numpy arrays in the range [0, 1]**:

* Grayscale image  → shape ``(H, W)``.
* Colour image     → shape ``(H, W, C)`` with C = 3 (RGB) or 4 (RGBA).

``0.0`` is black, ``1.0`` is white — i.e. the *tone* of the pixel.  Patterns
generally care about *ink coverage* which is ``1 - tone`` (dark = more ink);
:func:`coverage` provides that conversion.

PIL is used only at the boundary (decode/encode); the rest of the pipeline is
numpy-native so it stays backend-agnostic and easy to test.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

# Formats we explicitly advertise support for (PIL handles many more).
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")

# Rec. 601 luma weights for RGB → grayscale.
_LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float64)


def load_image(path: str | Path, *, mode: str | None = None) -> np.ndarray:
    """Load an image as a float64 array in [0, 1].

    ``mode`` optionally forces a PIL conversion before normalising:
      * ``"L"``    — grayscale, returns ``(H, W)``.
      * ``"RGB"``  — returns ``(H, W, 3)``.
      * ``"RGBA"`` — returns ``(H, W, 4)``.
      * ``None``   — keep the file's native mode (coerced to L/RGB/RGBA).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    img = Image.open(path)
    if mode is not None:
        img = img.convert(mode)
    elif img.mode not in ("L", "RGB", "RGBA"):
        # Coerce exotic modes (P, CMYK, I;16, …) to something predictable.
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    arr = np.asarray(img, dtype=np.float64) / 255.0
    return arr


def to_grayscale(arr: np.ndarray) -> np.ndarray:
    """Collapse any array to a 2-D grayscale tone map in [0, 1]."""
    if arr.ndim == 2:
        return arr
    if arr.ndim == 3:
        rgb = arr[..., :3]
        gray = rgb @ _LUMA
        if arr.shape[-1] == 4:  # premultiply over white using alpha
            alpha = arr[..., 3]
            gray = gray * alpha + (1.0 - alpha)
        return gray
    raise ValueError(f"unexpected array shape {arr.shape}")


def coverage(arr: np.ndarray) -> np.ndarray:
    """Ink coverage = ``1 - tone`` from a grayscale array (dark → 1.0)."""
    return 1.0 - to_grayscale(arr)


def save_image(arr: np.ndarray, path: str | Path) -> Path:
    """Save a float [0, 1] array (grayscale or RGB/RGBA) to disk."""
    path = Path(path)
    data = np.clip(arr, 0.0, 1.0)
    img = Image.fromarray((data * 255.0 + 0.5).astype(np.uint8))
    img.save(path)
    return path


def resize(arr: np.ndarray, *, max_side: int) -> np.ndarray:
    """Downscale so the longest side is at most ``max_side`` (keeps aspect)."""
    h, w = arr.shape[:2]
    longest = max(h, w)
    if longest <= max_side:
        return arr
    scale = max_side / longest
    new_size = (max(1, round(w * scale)), max(1, round(h * scale)))  # PIL is (W, H)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))
    img = img.resize(new_size, Image.LANCZOS)
    return np.asarray(img, dtype=np.float64) / 255.0
