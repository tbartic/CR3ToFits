from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import rawpy
from astropy.io import fits


def save_fits(image: np.ndarray, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    hdul = fits.PrimaryHDU(data=np.asarray(image))
    hdul.writeto(output_path, overwrite=True)
    return output_path


def convert_cr3_to_fits(input_path: str | Path, output_path: str | Path | None = None) -> Path:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"CR3 file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".fits")

    kwargs = {
        "half_size": False,
        "no_auto_bright": True,
        "use_camera_wb": True,
        "output_bps": 16,
    }

    color_space = getattr(getattr(rawpy, "ColorSpace", None), "sRGB", None)
    if color_space is not None:
        kwargs["output_color"] = color_space

    demosaic_algorithm = getattr(getattr(rawpy, "DemosaicingAlgorithm", None), "AHD", None)
    if demosaic_algorithm is not None:
        kwargs["demosaic_algorithm"] = demosaic_algorithm

    with rawpy.imread(str(input_path)) as raw:
        rgb = raw.postprocess(**kwargs)

    image = np.asarray(rgb)
    if image.ndim == 3:
        image = image[:, :, 0]

    return save_fits(image, output_path)


def convert_cr3_batch(
    input_paths: Iterable[str | Path],
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Exception]]]:
    converted = []
    failures = []
    for path in input_paths:
        input_path = Path(path)
        try:
            output_path = convert_cr3_to_fits(input_path)
        except Exception as exc:
            failures.append((input_path, exc))
        else:
            converted.append((input_path, output_path))
    return converted, failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Canon CR3 raw file to FITS.")
    parser.add_argument("input", type=str, help="Path to the input .cr3 file")
    parser.add_argument("-o", "--output", type=str, default=None, help="Optional output .fits path")
    args = parser.parse_args()

    output = convert_cr3_to_fits(args.input, args.output)
    print(f"Converted: {args.input} -> {output}")


if __name__ == "__main__":
    main()
