# CSV Insights

CSV Insights is a lightweight, GUI-based tool that allows users to quickly explore and analyze CSV files. With CSV Insights, you can load any CSV file, view descriptive statistics, inspect the first few rows, and compute correlation matrices for numeric columns. It's designed to be user-friendly for non-technical users and efficient for data analysts who need a rapid data overview.

---

## Features

- **Intuitive GUI:**  
  Easily browse and select any CSV file from your computer.
  
- **Descriptive Statistics:**  
  Generate a summary (count, mean, std, min, max, etc.) using `df.describe()`.

- **Data Preview:**  
  View the first 10 rows of your CSV file with `df.head()`.

- **Correlation Analysis:**  
  Compute and display a correlation matrix for numeric columns with `df.corr()`.

- **Real-Time Output:**  
  All results are displayed in a scrollable text area within the interface.

---

## How It Works

1. **Data Loading:**  
   The program uses Pandas to read a CSV file into a DataFrame.
   
2. **Data Analysis:**  
   - **Descriptive Statistics:** Generates summary statistics using `df.describe()`.
   - **Data Preview:** Displays the first few rows using `df.head()`.
   - **Correlation Analysis:** Computes correlations among numeric columns using `df.corr()`.
   
3. **Graphical Interface:**  
   Built with Tkinter, the GUI lets you select a CSV file, run various analysis functions via buttons, and view the output in a scrollable text area.

---

## Usage

1. **Run the Program:**  
   In your terminal or command prompt, navigate to the directory containing `csv_insights.py` and execute:

   python csv_insights.py
 
2. Select a CSV File:
Click the Browse button to choose the CSV file you wish to analyze.

3. Perform Analysis:
- Click "Show Summary" to display descriptive statistics.
- Click "Show Head" to preview the first 10 rows.
- Click "Show Correlations" to view the correlation matrix for numeric data.

4. View Results:
The output will be shown in the scrollable text area within the GUI.

## Troubleshooting
**CSV File Not Loading:**
- Verify the file is a properly formatted CSV file.
- Check for error messages in the GUI's log area.

**Data Analysis Issues:**
- Ensure your CSV file contains valid headers and data.
- Confirm that all dependencies (especially Pandas) are installed.

**General Errors:**
- Look at the log output in the GUI or the terminal for detailed error messages.
- Ensure you are running Python 3.x.

## Requirements
- Python 3.x
- Dependencies:
    pandas (install with pip install pandas)
    Tkinter (bundled with most Python installations)

## Installation
1. Install Python 3.x:
- Download and install from python.org.

2. Install Required Package:
- Open a terminal or command prompt and run:

pip install pandas

3. Download CSV Insights:
- Clone or download the script csv_insights.py from the repository.

## License
This project is provided "as is" without any warranty. Feel free to modify and use it as needed.