import csv
from tkinter import messagebox
from tkinter import filedialog

def export_to_csv(data, headers):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save Statement As"
    )

    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        messagebox.showinfo("Success", f"Statement downloaded successfully to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export statement:\n{e}")
