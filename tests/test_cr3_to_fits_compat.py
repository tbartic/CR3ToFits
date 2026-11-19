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

    def convert(path, output_path=None):
        if path == broken:
            raise ValueError("invalid CR3")
        return output_path or path.with_suffix(".fits")

    monkeypatch.setattr(cr3_to_fits, "convert_cr3_to_fits", convert)

    converted, failures = cr3_to_fits.convert_cr3_batch([first, broken, last])

    assert converted == [(first, first.with_suffix(".fits")), (last, last.with_suffix(".fits"))]
    assert failures[0][0] == broken
    assert str(failures[0][1]) == "invalid CR3"


def test_convert_cr3_batch_uses_output_directory(tmp_path: Path, monkeypatch):
    source = tmp_path / "source.CR3"
    output_directory = tmp_path / "fits"
    output_directory.mkdir()
    expected_output = output_directory / "source.fits"
    calls = []

    def convert(path, output_path):
        calls.append((path, output_path))
        return output_path

    monkeypatch.setattr(cr3_to_fits, "convert_cr3_to_fits", convert)
    progress = []

    converted, failures = cr3_to_fits.convert_cr3_batch(
        [source],
        output_directory,
        progress_callback=lambda completed, total, elapsed: progress.append((completed, total)),
    )

    assert converted == [(source, expected_output)]
    assert failures == []
    assert calls == [(source, expected_output)]
    assert progress == [(1, 1)]


def test_convert_cr3_batch_reports_duplicate_output_names(tmp_path: Path, monkeypatch):
    first = tmp_path / "first" / "same.CR3"
    second = tmp_path / "second" / "same.CR3"
    output_directory = tmp_path / "fits"
    calls = []

    def convert(path, output_path):
        calls.append(path)
        return output_path

    monkeypatch.setattr(cr3_to_fits, "convert_cr3_to_fits", convert)

    converted, failures = cr3_to_fits.convert_cr3_batch(
        [first, second],
        output_directory,
    )

    assert converted == [(first, output_directory / "same.fits")]
    assert len(failures) == 1
    assert failures[0][0] == second
    assert "same output" in str(failures[0][1])
    assert calls == [first]
