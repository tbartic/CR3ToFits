# CR3 to FITS Converter

This app converts Canon CR3 raw images to FITS using `rawpy` and `astropy`.

## Install

```powershell
py -3 -m pip install -r requirements.txt
```

## GUI

```powershell
py -3 app.py
```
```powershell
start_app.bat
```

Use **Browse** to select one or multiple CR3 files. For batch conversion, choose
an output folder or leave it empty to save each FITS file next to its source.
The progress bar shows estimated progress and remaining time. The custom output
path is available when converting a single file.

## Command line

```powershell
py -3 cr3_to_fits.py "C:\path\to\input.CR3" -o "C:\path\to\output.fits"
```

## Tests

```powershell
py -3 -m pytest -q
```
