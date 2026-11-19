from __future__ import annotations

from pathlib import Path

import numpy as np

from cr3_to_fits import save_fits


def test_save_fits_handles_simple_arrays(tmp_path: Path):
    image = np.array([[1, 2], [3, 4]], dtype=np.uint16)
    result = save_fits(image, tmp_path / "out.fits")

    assert result.exists()
    assert result.suffix.lower() == ".fits"
