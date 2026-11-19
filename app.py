from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from cr3_to_fits import convert_cr3_batch, convert_cr3_to_fits


conversion_queue: queue.Queue[tuple] = queue.Queue()
is_converting = False
progress_completed = 0
progress_total = 0
progress_average = 0.0
progress_last_completed_at = 0.0


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


def browse_batch_output() -> None:
    output_directory = filedialog.askdirectory(title="Select batch output folder", mustexist=True)
    if output_directory:
        batch_output_var.set(output_directory)


def update_output_controls() -> None:
    single_state = tk.NORMAL if input_listbox.size() <= 1 and not is_converting else tk.DISABLED
    batch_state = tk.NORMAL if input_listbox.size() > 1 and not is_converting else tk.DISABLED
    output_entry.configure(state=single_state)
    browse_output_button.configure(state=single_state)
    batch_output_entry.configure(state=batch_state)
    browse_batch_output_button.configure(state=batch_state)
    browse_input_button.configure(state=tk.DISABLED if is_converting else tk.NORMAL)
    convert_button.configure(state=tk.DISABLED if is_converting else tk.NORMAL)


def format_duration(seconds: float) -> str:
    seconds = max(0, round(seconds))
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def update_progress(completed: int, total: int, elapsed: float) -> None:
    global progress_completed, progress_total, progress_average, progress_last_completed_at
    progress_completed = completed
    progress_total = total
    progress_average = elapsed / completed
    progress_last_completed_at = time.monotonic()
    percent = int(completed / total * 100)
    progress_bar["value"] = completed / total * 100
    if completed == total:
        progress_label.configure(text=f"{completed}/{total} files | {percent}% complete")
    else:
        remaining = elapsed / completed * (total - completed)
        progress_label.configure(
            text=(
                f"{completed}/{total} files | {percent}% | "
                f"estimated {format_duration(remaining)} remaining"
            )
        )


def finish_conversion(converted: list, failures: list, total: int) -> None:
    global is_converting
    progress_bar.configure(maximum=100, value=100)
    update_progress(total, total, 0)
    is_converting = False
    update_output_controls()

    if failures:
        details = "\n".join(f"{path}: {error}" for path, error in failures)
        message = f"Converted {len(converted)} of {total} files.\n\nFailed files:\n{details}"
        if converted:
            messagebox.showwarning("Batch conversion completed with errors", message)
        else:
            messagebox.showerror("Batch conversion failed", message)
    elif total == 1:
        messagebox.showinfo("Success", f"FITS image saved to: {converted[0][1]}")
    else:
        messagebox.showinfo(
            "Batch conversion complete",
            f"Converted {len(converted)} files. FITS files were saved to "
            f"{batch_output_var.get() or 'their input folders'}.",
        )


def poll_conversion_queue(input_paths: tuple[str, ...], started_at: float) -> None:
    global is_converting
    try:
        while True:
            event = conversion_queue.get_nowait()
            if event[0] == "progress":
                update_progress(event[1], event[2], event[3])
            elif event[0] == "complete":
                finish_conversion(event[1], event[2], len(input_paths))
                return
            elif event[0] == "error":
                is_converting = False
                progress_label.configure(text="Conversion stopped.")
                update_output_controls()
                messagebox.showerror("Conversion failed", str(event[1]))
                return
    except queue.Empty:
        pass

    if is_converting:
        elapsed = format_duration(time.monotonic() - started_at)
        if len(input_paths) == 1:
            progress_label.configure(text=f"Converting 1/1 file | elapsed {elapsed}")
        elif progress_completed == 0:
            progress_label.configure(
                text=f"Converting 0/{len(input_paths)} files | elapsed {elapsed} | estimating..."
            )
        elif progress_completed < progress_total and progress_average > 0:
            current_file_elapsed = time.monotonic() - progress_last_completed_at
            current_file_progress = min(current_file_elapsed / progress_average, 0.99)
            estimated_progress = progress_completed + current_file_progress
            progress_bar["value"] = estimated_progress / progress_total * 100
            percent = int(estimated_progress / progress_total * 100)
            remaining = max(0, progress_average - current_file_elapsed)
            remaining += progress_average * (progress_total - progress_completed - 1)
            progress_label.configure(
                text=f"About {percent}% | estimated {format_duration(remaining)} remaining"
            )
    if is_converting:
        window.after(500, lambda: poll_conversion_queue(input_paths, started_at))


def run_conversion() -> None:
    global is_converting, progress_completed, progress_total, progress_average
    global progress_last_completed_at
    input_paths = tuple(input_listbox.get(0, tk.END))

    if not input_paths:
        messagebox.showwarning("Missing input", "Please choose at least one CR3 file.")
        return

    is_converting = True
    progress_completed = 0
    progress_total = len(input_paths)
    progress_average = 0.0
    progress_last_completed_at = time.monotonic()
    update_output_controls()
    progress_bar.configure(mode="determinate", maximum=100, value=0)
    started_at = time.monotonic()
    progress_label.configure(
        text=f"Converting 0/{len(input_paths)} files | estimating remaining time..."
    )
    output_path = output_entry.get().strip()
    output_directory = batch_output_var.get().strip() or None

    def convert_in_background() -> None:
        try:
            if len(input_paths) == 1:
                input_path = Path(input_paths[0])
                try:
                    output_file = convert_cr3_to_fits(input_path, output_path or None)
                    converted = [(input_path, output_file)]
                    failures = []
                except Exception as exc:
                    converted = []
                    failures = [(input_path, exc)]
                conversion_queue.put(("progress", 1, 1, time.monotonic() - started_at))
            else:
                converted, failures = convert_cr3_batch(
                    input_paths,
                    output_directory,
                    progress_callback=lambda completed, total, elapsed: conversion_queue.put(
                        ("progress", completed, total, elapsed)
                    ),
                )
            conversion_queue.put(("complete", converted, failures))
        except Exception as exc:
            conversion_queue.put(("error", exc))

    threading.Thread(target=convert_in_background, daemon=True).start()
    window.after(100, lambda: poll_conversion_queue(input_paths, started_at))


window = tk.Tk()
window.title("CR3 to FITS Converter")
window.geometry("760x500")
window.resizable(False, False)

frame = tk.Frame(window, padx=20, pady=20)
frame.pack(fill="both", expand=True)

input_label = tk.Label(frame, text="Input CR3 files (select multiple with Ctrl/Shift):")
input_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

input_listbox = tk.Listbox(frame, height=8, width=70, exportselection=False)
input_listbox.grid(row=1, column=0, padx=(0, 10), sticky="nsew")

browse_input_button = tk.Button(frame, text="Browse", command=browse_cr3)
browse_input_button.grid(row=1, column=1, sticky="e")

output_label = tk.Label(frame, text="Output FITS file (single input only):")
output_label.grid(row=2, column=0, sticky="w", pady=(12, 6))

output_entry = tk.Entry(frame, width=45)
output_entry.grid(row=3, column=0, padx=(0, 10), sticky="ew")

browse_output_button = tk.Button(frame, text="Browse", command=browse_output)
browse_output_button.grid(row=3, column=1, sticky="e")

batch_output_label = tk.Label(frame, text="Batch output folder (optional):")
batch_output_label.grid(row=4, column=0, sticky="w", pady=(12, 6))

batch_output_var = tk.StringVar()
batch_output_entry = tk.Entry(frame, textvariable=batch_output_var, width=45)
batch_output_entry.grid(row=5, column=0, padx=(0, 10), sticky="ew")

browse_batch_output_button = tk.Button(frame, text="Choose folder", command=browse_batch_output)
browse_batch_output_button.grid(row=5, column=1, sticky="e")

progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, mode="determinate")
progress_bar.grid(row=6, column=0, padx=(0, 10), pady=(18, 4), sticky="ew")

progress_label = tk.Label(frame, text="", anchor="w")
progress_label.grid(row=7, column=0, padx=(0, 10), sticky="ew")

convert_button = tk.Button(frame, text="Convert selected files", width=22, command=run_conversion)
convert_button.grid(row=8, column=0, columnspan=2, pady=(18, 0))

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)
update_output_controls()
window.mainloop()
