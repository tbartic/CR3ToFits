I created a minimal working app in the workspace:

GUI app: app.py
CLI converter: cr3_to_fits.py
test: test_cr3_to_fits.py
dependencies: requirements.txt
It uses rawpy to decode Canon CR3 files and astropy to write FITS output.

Run it
Install dependencies:
py -3 -m pip install -r requirements.txt

Open the GUI:
py -3 app.py

In the GUI, use Browse to select multiple CR3 files (Ctrl/Shift selects
non-adjacent or adjacent files), then choose Convert selected files. Batch
outputs are saved beside their input files. The optional output path applies
when converting a single file.

Or use the command line:
py -3 cr3_to_fits.py "C:\path\to\input.CR3" -o "C:\path\to\output.fits"

Verification
I verified it with fresh commands:

py -3 -m pytest -q → 1 passed in 1.66s
py -3 cr3_to_fits.py --help → displayed the expected CLI usage