from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from cr3_to_fits import convert_cr3_to_fits


def browse_cr3() -> None:
    path = filedialog.askopenfilename(filetypes=[("Canon CR3", "*.cr3 *.CR3")])
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)


def browse_output() -> None:
    output_path = filedialog.asksaveasfilename(defaultextension=".fits", filetypes=[("FITS", "*.fits")])
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)


def run_conversion() -> None:
    input_path = input_entry.get().strip()
    output_path = output_entry.get().strip()

    if not input_path:
        messagebox.showwarning("Missing input", "Please choose a CR3 file first.")
        return

    try:
        result = convert_cr3_to_fits(input_path, output_path or None)
        messagebox.showinfo("Success", f"FITS image saved to: {result}")
    except Exception as exc:  # pragma: no cover - UI exception handling
        messagebox.showerror("Conversion failed", str(exc))


window = tk.Tk()
window.title("CR3 to FITS Converter")
window.geometry("560x220")
window.resizable(False, False)

frame = tk.Frame(window, padx=20, pady=20)
frame.pack(fill="both", expand=True)

input_label = tk.Label(frame, text="Input CR3 file:")
input_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

input_entry = tk.Entry(frame, width=45)
input_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")

browse_input_button = tk.Button(frame, text="Browse", command=browse_cr3)
browse_input_button.grid(row=1, column=1, sticky="e")

output_label = tk.Label(frame, text="Output FITS file:")
output_label.grid(row=2, column=0, sticky="w", pady=(12, 6))

output_entry = tk.Entry(frame, width=45)
output_entry.grid(row=3, column=0, padx=(0, 10), sticky="ew")

browse_output_button = tk.Button(frame, text="Browse", command=browse_output)
browse_output_button.grid(row=3, column=1, sticky="e")

convert_button = tk.Button(frame, text="Convert", width=18, command=run_conversion)
convert_button.grid(row=4, column=0, columnspan=2, pady=(18, 0))

frame.columnconfigure(0, weight=1)
window.mainloop()
