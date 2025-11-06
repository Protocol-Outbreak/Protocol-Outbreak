# THIS IS A LIST OF ALL THE FONTS AVAILABLE, JUST RUN IT AND A NEW WINDOW POPS UP 

import tkinter as tk
from tkinter import font, ttk

root = tk.Tk()
root.title("Font Previewer")
root.geometry("800x600")

# Create a scrollable frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Display all fonts
for f_name in sorted(font.families()):
    lbl = tk.Label(
        scrollable_frame,
        text=f_name,
        font=(f_name, 18),
        pady=5
    )
    lbl.pack(anchor="w", padx=15)

root.mainloop()