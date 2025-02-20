import pandas as pd

# I'll assume you know how to install pandas ('pip install pandas')

# Load the CSV into a DataFrame
df = pd.read_csv("Insert_CSV") # Insert CSV file path

# Describe the data
print(df.describe())

# Ask me a question like:
# "Are there any correlations between age and spending_amount?" 
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd

class CSVInsightsGUI:
    def __init__(self, master):
        self.master = master
        master.title("CSV Insights")

        # File selection frame
        self.frame_file = tk.Frame(master)
        self.frame_file.pack(pady=10, padx=10, fill=tk.X)

        self.label_file = tk.Label(self.frame_file, text="CSV File:")
        self.label_file.pack(side=tk.LEFT)

        self.entry_file = tk.Entry(self.frame_file, width=50)
        self.entry_file.pack(side=tk.LEFT, padx=5)

        self.button_browse = tk.Button(self.frame_file, text="Browse", command=self.browse_file)
        self.button_browse.pack(side=tk.LEFT)

        # Buttons for analysis actions
        self.frame_buttons = tk.Frame(master)
        self.frame_buttons.pack(pady=5)

        self.button_summary = tk.Button(self.frame_buttons, text="Show Summary", command=self.show_summary)
        self.button_summary.pack(side=tk.LEFT, padx=5)

        self.button_head = tk.Button(self.frame_buttons, text="Show Head", command=self.show_head)
        self.button_head.pack(side=tk.LEFT, padx=5)

        self.button_corr = tk.Button(self.frame_buttons, text="Show Correlations", command=self.show_correlations)
        self.button_corr.pack(side=tk.LEFT, padx=5)

        # Scrollable text widget for output
        self.text_output = scrolledtext.ScrolledText(master, width=80, height=20, state=tk.DISABLED)
        self.text_output.pack(pady=10, padx=10)

        self.df = None  # DataFrame placeholder

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, file_path)
            try:
                self.df = pd.read_csv(file_path)
                messagebox.showinfo("File Loaded", f"Loaded CSV file with {len(self.df)} rows and {len(self.df.columns)} columns.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")
                self.df = None

    def show_summary(self):
        if self.df is None:
            messagebox.showerror("Error", "No CSV file loaded.")
            return
        summary = self.df.describe(include='all')
        self.display_text(summary.to_string())

    def show_head(self):
        if self.df is None:
            messagebox.showerror("Error", "No CSV file loaded.")
            return
        head = self.df.head(10)
        self.display_text(head.to_string())

    def show_correlations(self):
        if self.df is None:
            messagebox.showerror("Error", "No CSV file loaded.")
            return
        try:
            corr = self.df.corr()
            self.display_text(corr.to_string())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute correlations:\n{e}")

    def display_text(self, text):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        self.text_output.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVInsightsGUI(root)
    root.mainloop()