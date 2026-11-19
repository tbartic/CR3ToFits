from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Callable, Iterable

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
    output_directory: str | Path | None = None,
    progress_callback: Callable[[int, int, float], None] | None = None,
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Exception]]]:
    input_paths = list(input_paths)
    converted = []
    failures = []
    output_paths = set()
    started_at = time.perf_counter()
    for completed, path in enumerate(input_paths, 1):
        input_path = Path(path)
        try:
            output_path = (
                Path(output_directory) / input_path.with_suffix(".fits").name
                if output_directory is not None
                else None
            )
            target_path = output_path or input_path.with_suffix(".fits")
            if target_path in output_paths:
                raise ValueError(f"Multiple input files map to the same output: {target_path}")
            result = convert_cr3_to_fits(input_path, output_path)
        except Exception as exc:
            failures.append((input_path, exc))
        else:
            output_paths.add(target_path)
            converted.append((input_path, result))
        finally:
            if progress_callback is not None:
                progress_callback(completed, len(input_paths), time.perf_counter() - started_at)
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
