from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from cr3_to_fits import convert_cr3_batch, convert_cr3_to_fits


def browse_cr3() -> None:
    paths = filedialog.askopenfilenames(
        title="Select CR3 files",
        filetypes=[("Canon CR3", "*.cr3 *.CR3")],
    )
    if paths:
        input_listbox.delete(0, tk.END)
        for path in paths:
            input_listbox.insert(tk.END, path)
        update_output_controls()


def browse_output() -> None:
    output_path = filedialog.asksaveasfilename(defaultextension=".fits", filetypes=[("FITS", "*.fits")])
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)


def update_output_controls() -> None:
    state = tk.DISABLED if input_listbox.size() > 1 else tk.NORMAL
    output_entry.configure(state=state)
    browse_output_button.configure(state=state)


def run_conversion() -> None:
    input_paths = input_listbox.get(0, tk.END)
    output_path = output_entry.get().strip()

    if not input_paths:
        messagebox.showwarning("Missing input", "Please choose at least one CR3 file.")
        return

    if len(input_paths) == 1:
        try:
            result = convert_cr3_to_fits(input_paths[0], output_path or None)
            messagebox.showinfo("Success", f"FITS image saved to: {result}")
        except Exception as exc:  # pragma: no cover - UI exception handling
            messagebox.showerror("Conversion failed", str(exc))
        return

    converted, failures = convert_cr3_batch(input_paths)
    if failures:
        details = "\n".join(f"{path}: {error}" for path, error in failures)
        message = f"Converted {len(converted)} of {len(input_paths)} files.\n\nFailed files:\n{details}"
        if converted:
            messagebox.showwarning("Batch conversion completed with errors", message)
        else:
            messagebox.showerror("Batch conversion failed", message)
    else:
        messagebox.showinfo(
            "Batch conversion complete",
            f"Converted {len(converted)} files. FITS files were saved next to their CR3 files.",
        )


window = tk.Tk()
window.title("CR3 to FITS Converter")
window.geometry("640x390")
window.resizable(False, False)

frame = tk.Frame(window, padx=20, pady=20)
frame.pack(fill="both", expand=True)

input_label = tk.Label(frame, text="Input CR3 files (select multiple with Ctrl/Shift):")
input_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

input_listbox = tk.Listbox(frame, height=8, width=70, exportselection=False)
input_listbox.grid(row=1, column=0, padx=(0, 10), sticky="nsew")

browse_input_button = tk.Button(frame, text="Browse", command=browse_cr3)
browse_input_button.grid(row=1, column=1, sticky="e")

output_label = tk.Label(frame, text="Output FITS file (single input only; batch uses input folders):")
output_label.grid(row=2, column=0, sticky="w", pady=(12, 6))

output_entry = tk.Entry(frame, width=45)
output_entry.grid(row=3, column=0, padx=(0, 10), sticky="ew")

browse_output_button = tk.Button(frame, text="Browse", command=browse_output)
browse_output_button.grid(row=3, column=1, sticky="e")

convert_button = tk.Button(frame, text="Convert selected files", width=22, command=run_conversion)
convert_button.grid(row=4, column=0, columnspan=2, pady=(18, 0))

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)
window.mainloop()
