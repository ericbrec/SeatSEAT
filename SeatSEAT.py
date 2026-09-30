import tkinter as tk
from tkinter import ttk, font
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import tkinterweb
from HTMLClipboard import PutHtml
import markdown
from allocator import Allocator

class SeatSEAT(tk.Tk):
    def __init__(self, *args, **kw):
        tk.Tk.__init__(self, *args, **kw)
        self.title("SeatSEAT")
        self.geometry("1100x850")
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.allocator = Allocator()

        # --- Top Frames (Participants / Ticket Allocation) ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left column
        left_frame = ttk.Frame(top_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        participants_label = ttk.Label(left_frame, text="Participants")
        participants_label.pack(pady=(0, 5))

        self.participants_html = tkinterweb.HtmlFrame(left_frame, textwrap=False, horizontal_scrollbar="auto")
        self.participants_html.pack(fill="both", expand=True)

        load_btn = ttk.Button(left_frame, text="Load Participants", command=self.load_participants)
        load_btn.pack(pady=(5, 0))

        # Right column
        right_frame = ttk.Frame(top_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        allocation_label = ttk.Label(right_frame, text="Ticket Allocation")
        allocation_label.pack(pady=(0, 5))

        self.allocation_html = tkinterweb.HtmlFrame(right_frame, textwrap=False, horizontal_scrollbar="auto")
        self.allocation_html.pack(fill="both", expand=True)

        allocate_btn = ttk.Button(right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        allocate_btn.pack(pady=(5, 0))

        # Make columns expand evenly
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(0, weight=1)

        # --- Error Report Section ---
        error_frame = ttk.Frame(self)
        error_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        error_label = ttk.Label(error_frame, text="Errors")
        error_label.pack(anchor="c", pady=(0, 5))

        self.error_box = ScrolledText(error_frame, wrap="word")
        self.error_box.pack(fill="both", expand=True)

    def format_report(self, snippet):
        return f"""
            <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
                padding: 2px;
            }}
            </style>
            {snippet}
        """

    def load_participants(self):
        directory = filedialog.askdirectory(title="Load Participants")
        if directory:
            self.allocator.LoadSchedule(directory)
            self.allocator.LoadFans()
            self.participants_html.load_html(self.format_report(markdown.markdown(self.allocator.GameRankingReport(), extensions=['tables'])))
            self.allocator.AllocateTickets()
            self.allocation_html.load_html(self.format_report(markdown.markdown(self.allocator.GameAllocationReport(), extensions=['tables'])))
            self.error_box.delete('1.0', 'end')
            self.error_box.insert('end', self.allocator.errorReport)

    def copy_to_clipboard(self):
        PutHtml(self.allocation_html.save_page())

if __name__ == "__main__":
    app = SeatSEAT()
    app.mainloop()