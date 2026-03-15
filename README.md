# CSV Insights

A lightweight, GUI-based tool for exploring and analyzing CSV files. Load any CSV, view statistics, spot missing data, visualize distributions, and export results, all from a clean Tkinter interface.

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

---

## Features

- **Modern themed UI** - ttk widgets, sidebar with grouped sections, tabbed output (Text + Chart), status bar, menu bar
- **Smart CSV loading** - auto-detects delimiter and encoding via `csv.Sniffer`; manual overrides for delimiter, encoding, header row, and skip rows
- **Data exploration** - data info, head, tail, summary statistics, value counts, missing values report, correlation matrix
- **Embedded charts** - histogram, scatter plot, correlation heatmap, value counts bar chart (matplotlib, embedded via `FigureCanvasTkAgg`)
- **Export** - save data as CSV, copy text to clipboard, export text output, save charts as PNG/SVG/PDF
- **Keyboard shortcuts** - `Ctrl+O` open, `Ctrl+E` export CSV, `Ctrl+F` find in output, `Ctrl+Q` quit
- **Search** - find and highlight text in the output area
- **Right-click context menu** - Select All and Copy on the text output

---

## Installation

1. **Python 3.9+** required: [python.org](https://www.python.org/)

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   This installs `pandas` and `matplotlib`. Tkinter is bundled with standard Python installations.

---

## Usage

```bash
python CSVinsights.py
```

1. **Open a file** - click **Browse** or press `Ctrl+O` to select a CSV, TSV, or TXT file.
2. **Explore data** - use the sidebar buttons: Data Info, Head, Tail, Summary Stats.
3. **Analyze** - Correlations, Value Counts (per selected column), Missing Values.
4. **Visualize** - select a column from the dropdown, then click Histogram, Scatter Plot, Corr Heatmap, or Value Counts Chart. Charts appear in the Chart tab.
5. **Configure loading** - click **Options** in the toolbar to set delimiter, encoding, header, and skip rows, then **Reload**.
6. **Export** - Export CSV, Export Text, Copy to Clipboard, or Save Chart from the sidebar or File menu.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open CSV file |
| `Ctrl+E` | Export data as CSV |
| `Ctrl+F` | Find in output |
| `Ctrl+Q` | Quit |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | >= 1.5 | Data loading and analysis |
| `matplotlib` | >= 3.5 | Embedded charts |
| `tkinter` | bundled | GUI (included with Python) |

---

## License

This project is provided "as is" without any warranty. Feel free to modify and use it as needed.
