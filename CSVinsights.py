"""CSVinsights - A lightweight CSV explorer with analysis and visualization."""

import csv
import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_TITLE = "CSV Insights"
VERSION = "1.0.0"
MIN_WIDTH, MIN_HEIGHT = 900, 650
MONO_FONT = ("Consolas", 10)
DELIMITERS = {",": ",", ";": ";", "Tab": "\t", "|": "|", "Custom": None}
ENCODINGS = ["utf-8", "latin-1", "cp1252", "utf-16"]
DEFAULT_HEAD_TAIL = 10
HEATMAP_MAX_COLS = 30
pd.set_option("display.width", 2000)
pd.set_option("display.max_columns", 100)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class CSVInsightsApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.protocol("WM_DELETE_WINDOW", self._on_quit)

        self.df: Optional[pd.DataFrame] = None
        self.file_path: str = ""
        self._current_figure: Optional[Figure] = None

        style = ttk.Style()
        style.theme_use("vista" if "vista" in style.theme_names() else "clam")

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_menubar()
        self._build_toolbar()
        self._build_sidebar()
        self._build_output()
        self._build_statusbar()
        self._bind_shortcuts()
        self._center_window()

    # -- Layout builders ----------------------------------------------------

    def _build_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open\u2026", accelerator="Ctrl+O", command=self.browse_file)
        file_menu.add_command(label="Reload", command=self.reload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV\u2026", accelerator="Ctrl+E", command=self.export_csv)
        file_menu.add_command(label="Export Text\u2026", command=self.export_text)
        file_menu.add_command(label="Save Chart\u2026", command=self.save_chart)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q", command=self._on_quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy to Clipboard", command=self.copy_to_clipboard)
        edit_menu.add_command(label="Find\u2026", accelerator="Ctrl+F", command=self._focus_search)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def _center_window(self):
        self.root.update_idletasks()
        w = max(self.root.winfo_width(), MIN_WIDTH)
        h = max(self.root.winfo_height(), MIN_HEIGHT)
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(toolbar, text="CSV File:").pack(side=tk.LEFT)
        self.entry_file = ttk.Entry(toolbar, width=50)
        self.entry_file.pack(side=tk.LEFT, padx=(4, 2))
        ttk.Button(toolbar, text="Browse\u2026", command=self.browse_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reload", command=self.reload_file).pack(side=tk.LEFT, padx=2)

        # --- Advanced CSV options (collapsible) ---
        self._opts_visible = tk.BooleanVar(value=False)
        self._toggle_btn = ttk.Button(toolbar, text="Options \u25b6", width=10,
                                       command=self._toggle_options)
        self._toggle_btn.pack(side=tk.LEFT, padx=(10, 2))

        self._opts_frame = ttk.Frame(toolbar)
        # Delimiter
        ttk.Label(self._opts_frame, text="Delim:").pack(side=tk.LEFT, padx=(4, 0))
        self.delim_var = tk.StringVar(value=",")
        self._delim_combo = ttk.Combobox(self._opts_frame, textvariable=self.delim_var,
                                          values=list(DELIMITERS.keys()), width=6, state="readonly")
        self._delim_combo.pack(side=tk.LEFT, padx=2)
        self.custom_delim = ttk.Entry(self._opts_frame, width=3)
        self.custom_delim.pack(side=tk.LEFT)
        self.custom_delim.insert(0, ",")

        # Encoding
        ttk.Label(self._opts_frame, text="Enc:").pack(side=tk.LEFT, padx=(6, 0))
        self.enc_var = tk.StringVar(value="utf-8")
        ttk.Combobox(self._opts_frame, textvariable=self.enc_var,
                      values=ENCODINGS, width=8, state="readonly").pack(side=tk.LEFT, padx=2)

        # Header
        self.header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self._opts_frame, text="Header", variable=self.header_var).pack(side=tk.LEFT, padx=4)

        # Skip rows
        ttk.Label(self._opts_frame, text="Skip rows:").pack(side=tk.LEFT, padx=(4, 0))
        self.skip_var = tk.StringVar(value="0")
        ttk.Entry(self._opts_frame, textvariable=self.skip_var, width=4).pack(side=tk.LEFT, padx=2)

    def _toggle_options(self):
        if self._opts_visible.get():
            self._opts_frame.pack_forget()
            self._toggle_btn.config(text="Options \u25b6")
            self._opts_visible.set(False)
        else:
            self._opts_frame.pack(side=tk.LEFT)
            self._toggle_btn.config(text="Options \u25c0")
            self._opts_visible.set(True)

    def _build_sidebar(self):
        sidebar = ttk.Frame(self.root, padding=4)
        sidebar.grid(row=1, column=0, sticky="ns")

        # Column selector
        col_frame = ttk.LabelFrame(sidebar, text="Column", padding=4)
        col_frame.pack(fill=tk.X, pady=(0, 6))
        self.col_var = tk.StringVar()
        self.col_combo = ttk.Combobox(col_frame, textvariable=self.col_var, state="readonly", width=18)
        self.col_combo.pack(fill=tk.X)

        # Data section
        data_frame = ttk.LabelFrame(sidebar, text="Data", padding=4)
        data_frame.pack(fill=tk.X, pady=(0, 6))
        for text, cmd in [
            ("Data Info", self.show_info),
            ("Head (first 10)", self.show_head),
            ("Tail (last 10)", self.show_tail),
            ("Summary Stats", self.show_summary),
        ]:
            ttk.Button(data_frame, text=text, command=cmd).pack(fill=tk.X, pady=1)

        # Statistics section
        stats_frame = ttk.LabelFrame(sidebar, text="Statistics", padding=4)
        stats_frame.pack(fill=tk.X, pady=(0, 6))
        for text, cmd in [
            ("Correlations", self.show_correlations),
            ("Value Counts", self.show_value_counts),
            ("Missing Values", self.show_missing),
        ]:
            ttk.Button(stats_frame, text=text, command=cmd).pack(fill=tk.X, pady=1)

        # Visualization section
        viz_frame = ttk.LabelFrame(sidebar, text="Visualize", padding=4)
        viz_frame.pack(fill=tk.X, pady=(0, 6))
        for text, cmd in [
            ("Histogram", self.plot_histogram),
            ("Scatter Plot", self.plot_scatter),
            ("Corr Heatmap", self.plot_heatmap),
            ("Value Counts Chart", self.plot_value_counts_chart),
        ]:
            ttk.Button(viz_frame, text=text, command=cmd).pack(fill=tk.X, pady=1)

        # Scatter Y column
        scatter_y_frame = ttk.LabelFrame(sidebar, text="Scatter Y Column", padding=4)
        scatter_y_frame.pack(fill=tk.X, pady=(0, 6))
        self.scatter_y_var = tk.StringVar()
        self.scatter_y_combo = ttk.Combobox(scatter_y_frame, textvariable=self.scatter_y_var,
                                             state="readonly", width=18)
        self.scatter_y_combo.pack(fill=tk.X)

        # Export section
        export_frame = ttk.LabelFrame(sidebar, text="Export", padding=4)
        export_frame.pack(fill=tk.X, pady=(0, 6))
        for text, cmd in [
            ("Export CSV\u2026", self.export_csv),
            ("Export Text\u2026", self.export_text),
            ("Copy to Clipboard", self.copy_to_clipboard),
            ("Save Chart\u2026", self.save_chart),
        ]:
            ttk.Button(export_frame, text=text, command=cmd).pack(fill=tk.X, pady=1)

    def _build_output(self):
        out_frame = ttk.Frame(self.root, padding=4)
        out_frame.grid(row=1, column=1, sticky="nsew")
        out_frame.rowconfigure(1, weight=1)
        out_frame.columnconfigure(0, weight=1)

        # Search bar
        search_frame = ttk.Frame(out_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self._search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self._search_entry.pack(side=tk.LEFT, padx=4)
        self._search_entry.bind("<Return>", lambda e: self.search_output())
        ttk.Button(search_frame, text="Find", command=self.search_output).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT, padx=2)

        # Notebook (Text + Chart tabs)
        self.notebook = ttk.Notebook(out_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        # Text tab
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="  Text  ")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        self.text_output = tk.Text(text_frame, wrap=tk.NONE, state=tk.DISABLED,
                                    font=MONO_FONT)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        # Scrollbars
        yscroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_output.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_output.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self.text_output.config(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.text_output.tag_configure("search_hl", background="yellow", foreground="black")

        # Right-click context menu
        self._text_ctx_menu = tk.Menu(self.text_output, tearoff=0)
        self._text_ctx_menu.add_command(label="Select All", command=self._select_all_text)
        self._text_ctx_menu.add_command(label="Copy", command=self._copy_selection)
        self.text_output.bind("<Button-3>", self._show_text_context_menu)

        # Chart tab
        chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(chart_frame, text="  Chart  ")
        chart_frame.rowconfigure(0, weight=1)
        chart_frame.columnconfigure(0, weight=1)
        self._chart_frame = chart_frame
        self._chart_canvas: Optional[FigureCanvasTkAgg] = None

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="No file loaded")
        status = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                            padding=(6, 2))
        status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.browse_file())
        self.root.bind("<Control-e>", lambda e: self.export_csv())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Control-q>", lambda e: self._on_quit())

    def _focus_search(self):
        self.search_var.set("")
        self.notebook.select(0)
        self._search_entry.focus_set()

    def _on_quit(self):
        if self._current_figure is not None:
            self._current_figure.clear()
            self._current_figure = None
        self.root.destroy()

    def _show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE} v{VERSION}\n\nA lightweight CSV explorer.")

    def _show_text_context_menu(self, event):
        self._text_ctx_menu.tk_popup(event.x_root, event.y_root)

    def _select_all_text(self):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.tag_add(tk.SEL, "1.0", tk.END)
        self.text_output.config(state=tk.DISABLED)

    def _copy_selection(self):
        try:
            sel = self.text_output.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(sel)
        except tk.TclError:
            pass  # No selection

    # -- Helpers ------------------------------------------------------------

    def _require_data(self) -> bool:
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return False
        return True

    def display_text(self, text: str):
        self.notebook.select(0)
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, text)
        self.text_output.config(state=tk.DISABLED)

    def display_chart(self, fig: Figure):
        if self._current_figure is not None:
            self._current_figure.clear()
        self._current_figure = fig
        if self._chart_canvas is not None:
            self._chart_canvas.get_tk_widget().destroy()
        self._chart_canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
        self._chart_canvas.draw()
        self._chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.notebook.select(1)

    def update_status(self, msg: str):
        self.status_var.set(msg)

    def update_column_list(self):
        if self.df is not None:
            cols = list(self.df.columns)
            self.col_combo["values"] = cols
            self.scatter_y_combo["values"] = cols
            if cols:
                self.col_combo.current(0)
                self.scatter_y_combo.current(min(1, len(cols) - 1))
        else:
            self.col_combo["values"] = []
            self.scatter_y_combo["values"] = []

    # -- File operations ----------------------------------------------------

    def _get_load_kwargs(self) -> dict:
        kwargs: dict = {}
        # Delimiter
        delim_label = self.delim_var.get()
        if delim_label == "Custom":
            d = self.custom_delim.get()
            if d:
                kwargs["sep"] = d
        else:
            kwargs["sep"] = DELIMITERS.get(delim_label, ",")
        # Encoding
        kwargs["encoding"] = self.enc_var.get()
        # Header
        if not self.header_var.get():
            kwargs["header"] = None
        # Skip rows
        try:
            skip = int(self.skip_var.get())
            if skip > 0:
                kwargs["skiprows"] = skip
        except ValueError:
            pass
        return kwargs

    def _auto_detect_and_load(self, path: str) -> pd.DataFrame:
        """Try loading with auto-detection, fall back to user-specified options."""
        # If user has explicitly set non-default options, use those directly
        if self._opts_visible.get():
            return pd.read_csv(path, **self._get_load_kwargs())

        # Auto-detect delimiter
        detected_sep = ","
        detected_enc = "utf-8"
        for enc in ["utf-8", "latin-1"]:
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    sample = f.read(8192)
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                detected_sep = dialect.delimiter
                detected_enc = enc
                break
            except Exception:
                detected_enc = enc
                continue

        # Try detected encoding, then fall back
        for enc in [detected_enc, "utf-8", "latin-1"]:
            try:
                return pd.read_csv(path, sep=detected_sep, encoding=enc)
            except Exception:
                continue

        # Final fallback: let pandas figure it out
        return pd.read_csv(path)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("TSV Files", "*.tsv"),
                       ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, path)
            self._load_file(path)

    def reload_file(self):
        path = self.entry_file.get().strip()
        if not path:
            messagebox.showwarning("No File", "No file path to reload.")
            return
        self._load_file(path)

    def _load_file(self, path: str):
        try:
            self.df = self._auto_detect_and_load(path)
            self.file_path = path
            self.update_column_list()
            fname = os.path.basename(path)
            rows, cols = self.df.shape
            self.update_status(f"{fname}  |  {rows:,} rows \u00d7 {cols} columns")
            self.show_head()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")
            self.df = None
            self.update_status("Error loading file")

    # -- Analysis -----------------------------------------------------------

    def show_info(self):
        if not self._require_data():
            return
        buf = io.StringIO()
        self.df.info(buf=buf, memory_usage="deep")
        info_text = buf.getvalue()

        dupes = self.df.duplicated().sum()
        info_text += f"\n\nDuplicate rows: {dupes:,}"
        self.display_text(info_text)

    def show_summary(self):
        if not self._require_data():
            return
        summary = self.df.describe(include="all")
        self.display_text(summary.to_string())

    def show_head(self):
        if not self._require_data():
            return
        self.display_text(self.df.head(DEFAULT_HEAD_TAIL).to_string())

    def show_tail(self):
        if not self._require_data():
            return
        self.display_text(self.df.tail(DEFAULT_HEAD_TAIL).to_string())

    def show_correlations(self):
        if not self._require_data():
            return
        try:
            corr = self.df.corr(numeric_only=True)
            self.display_text(corr.to_string())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute correlations:\n{e}")

    def show_value_counts(self):
        if not self._require_data():
            return
        col = self.col_var.get()
        if not col:
            messagebox.showwarning("No Column", "Select a column first.")
            return
        vc = self.df[col].value_counts()
        self.display_text(f"Value counts for '{col}':\n\n{vc.to_string()}")

    def show_missing(self):
        if not self._require_data():
            return
        total = self.df.isnull().sum().sort_values(ascending=False)
        pct = (total / len(self.df) * 100).round(2)
        report = pd.DataFrame({"Missing": total, "Percent": pct})
        report = report[report["Missing"] > 0]
        if report.empty:
            self.display_text("No missing values found.")
        else:
            self.display_text(f"Missing values:\n\n{report.to_string()}")

    # -- Visualization ------------------------------------------------------

    def plot_histogram(self):
        if not self._require_data():
            return
        col = self.col_var.get()
        if not col:
            messagebox.showwarning("No Column", "Select a column first.")
            return
        if not pd.api.types.is_numeric_dtype(self.df[col]):
            messagebox.showwarning("Not Numeric", f"'{col}' is not a numeric column.")
            return
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.hist(self.df[col].dropna(), bins=30, edgecolor="black", alpha=0.8)
        ax.set_title(f"Histogram of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        self.display_chart(fig)

    def plot_scatter(self):
        if not self._require_data():
            return
        x_col = self.col_var.get()
        y_col = self.scatter_y_var.get()
        if not x_col or not y_col:
            messagebox.showwarning("Select Columns", "Select both X (Column) and Y (Scatter Y Column).")
            return
        for c in (x_col, y_col):
            if not pd.api.types.is_numeric_dtype(self.df[c]):
                messagebox.showwarning("Not Numeric", f"'{c}' is not a numeric column.")
                return
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(self.df[x_col], self.df[y_col], alpha=0.5, s=15, edgecolors="none")
        ax.set_title(f"{x_col} vs {y_col}")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        fig.tight_layout()
        self.display_chart(fig)

    def plot_heatmap(self):
        if not self._require_data():
            return
        corr = self.df.corr(numeric_only=True)
        if corr.empty:
            messagebox.showwarning("No Data", "No numeric columns to correlate.")
            return
        if len(corr.columns) > HEATMAP_MAX_COLS:
            corr = corr.iloc[:HEATMAP_MAX_COLS, :HEATMAP_MAX_COLS]
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        im = ax.imshow(corr.values, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(corr.columns, fontsize=8)
        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("Correlation Heatmap")
        fig.tight_layout()
        self.display_chart(fig)

    def plot_value_counts_chart(self):
        if not self._require_data():
            return
        col = self.col_var.get()
        if not col:
            messagebox.showwarning("No Column", "Select a column first.")
            return
        vc = self.df[col].value_counts().head(20).sort_values()
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh([str(v) for v in vc.index], vc.values, edgecolor="black", alpha=0.8)
        ax.set_title(f"Top {len(vc)} values in '{col}'")
        ax.set_xlabel("Count")
        fig.tight_layout()
        self.display_chart(fig)

    # -- Export -------------------------------------------------------------

    def export_csv(self):
        if not self._require_data():
            return
        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if path:
            try:
                self.df.to_csv(path, index=False)
                self.update_status(f"Exported CSV to {path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def export_text(self):
        content = self.text_output.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("No Content", "Nothing to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Text",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.update_status(f"Exported text to {path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def copy_to_clipboard(self):
        content = self.text_output.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("No Content", "Nothing to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.update_status("Copied to clipboard")

    def save_chart(self):
        if self._current_figure is None:
            messagebox.showwarning("No Chart", "No chart to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Chart",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("SVG Image", "*.svg"),
                       ("PDF Document", "*.pdf"), ("All Files", "*.*")]
        )
        if path:
            try:
                self._current_figure.savefig(path, dpi=150, bbox_inches="tight")
                self.update_status(f"Chart saved to {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    # -- Search -------------------------------------------------------------

    def search_output(self):
        query = self.search_var.get()
        if not query:
            return
        self.text_output.tag_remove("search_hl", "1.0", tk.END)
        start = "1.0"
        count = 0
        while True:
            pos = self.text_output.search(query, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.text_output.tag_add("search_hl", pos, end)
            start = end
            count += 1
        if count == 0:
            self.update_status(f"No matches for '{query}'")
        else:
            self.update_status(f"{count} match{'es' if count != 1 else ''} for '{query}'")
            self.text_output.see("search_hl.first")

    def _clear_search(self):
        self.search_var.set("")
        self.text_output.tag_remove("search_hl", "1.0", tk.END)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    CSVInsightsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
