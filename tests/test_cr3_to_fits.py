from pathlib import Path

import numpy as np
from astropy.io import fits

from cr3_to_fits import save_fits


def test_save_fits_creates_a_valid_fits_file(tmp_path: Path):
    output_path = tmp_path / "output.fits"
    image = np.array([[1, 2], [3, 4]], dtype=np.uint16)

    save_fits(image, output_path)

    assert output_path.exists()
    with fits.open(output_path) as hdul:
        assert np.array_equal(hdul[0].data, image)
