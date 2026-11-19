from __future__ import annotations

from pathlib import Path

import numpy as np

import cr3_to_fits
from cr3_to_fits import save_fits


def test_save_fits_handles_simple_arrays(tmp_path: Path):
    image = np.array([[1, 2], [3, 4]], dtype=np.uint16)
    result = save_fits(image, tmp_path / "out.fits")

    assert result.exists()
    assert result.suffix.lower() == ".fits"


def test_convert_cr3_batch_continues_after_a_file_fails(tmp_path: Path, monkeypatch):
    first = tmp_path / "first.CR3"
    broken = tmp_path / "broken.CR3"
    last = tmp_path / "last.CR3"

    def convert(path):
        if path == broken:
            raise ValueError("invalid CR3")
        return path.with_suffix(".fits")

    monkeypatch.setattr(cr3_to_fits, "convert_cr3_to_fits", convert)

    converted, failures = cr3_to_fits.convert_cr3_batch([first, broken, last])

    assert converted == [(first, first.with_suffix(".fits")), (last, last.with_suffix(".fits"))]
    assert failures[0][0] == broken
    assert str(failures[0][1]) == "invalid CR3"
