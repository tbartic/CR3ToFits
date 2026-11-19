# CR3toFITS

CR3toFITS is a minimal working app for converting Canon CR3 files to FITS.

GUI app: app.py
CLI converter: cr3_to_fits.py
test: test_cr3_to_fits.py
dependencies: requirements.txt
It uses rawpy to decode Canon CR3 files and astropy to write FITS output.

## Run it

Install dependencies:
py -3 -m pip install -r requirements.txt

### Open the GUI:
py -3 app.py
OR
run start_app.bat

In the GUI, use Browse to select multiple CR3 files (Ctrl/Shift selects
non-adjacent or adjacent files), then choose Convert selected files. Batch
outputs are saved beside their input files. The optional output path applies
when converting a single file.

### Use the command line:

File conversion

py -3 cr3_to_fits.py [-h] [-o OUTPUT] input
py -3 cr3_to_fits.py "C:\path\to\input.CR3" -o "C:\path\to\output.fits"

Options:

  -h, --help           show this help message and exit
  -o, --output OUTPUT  Optional output .fits path

