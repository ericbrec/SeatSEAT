import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import tkinterweb

def create_app():
    root = tk.Tk()
    root.title("SeatSEAT")
    root.geometry("1100x800")

    # --- Top Frames (Participants / Ticket Allocation) ---
    top_frame = ttk.Frame(root)
    top_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Left column
    left_frame = ttk.Frame(top_frame)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    participants_label = ttk.Label(left_frame, text="Participants", font=("Arial", 14, "bold"))
    participants_label.pack(pady=(0, 5))

    participants_html = tkinterweb.HtmlFrame(left_frame, horizontal_scrollbar="auto")
    participants_html.pack(fill="both", expand=True)

    load_btn = ttk.Button(left_frame, text="Load Participants")
    load_btn.pack(pady=10)

    # Right column
    right_frame = ttk.Frame(top_frame)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    allocation_label = ttk.Label(right_frame, text="Ticket Allocation", font=("Arial", 14, "bold"))
    allocation_label.pack(pady=(0, 5))

    allocation_html = tkinterweb.HtmlFrame(right_frame, horizontal_scrollbar="auto")
    allocation_html.pack(fill="both", expand=True)

    allocate_btn = ttk.Button(right_frame, text="Copy to Clipboard")
    allocate_btn.pack(pady=10)

    # Make columns expand evenly
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)
    top_frame.rowconfigure(0, weight=1)

    # --- Error Report Section ---
    error_frame = ttk.Frame(root)
    error_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    error_label = ttk.Label(error_frame, text="Error Report", font=("Arial", 14, "bold"))
    error_label.pack(anchor="w")

    error_box = ScrolledText(error_frame, height=12, wrap="word")
    error_box.pack(fill="both", expand=True)

    return root

if __name__ == "__main__":
    app = create_app()
    app.mainloop()