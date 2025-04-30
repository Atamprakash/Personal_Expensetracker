import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import os

FILE_NAME = 'transactions.csv'

# Ensure CSV file exists
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Type', 'Amount', 'Description'])

# GUI App Class
class ExpenseTracker:
    def __init__(self, window):    #constructor in python [Window Loop]
        self.window = window
        self.window.title("Personal Expense Tracker")
        self.window.geometry("1000x500")
        self.window.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.window, text="Expense Tracker", font=("Arial", 20, 'bold'))
        title.pack(pady=10)

        # Frame for entry fields
        entry_frame = tk.Frame(self.window) #Little Frame of Text side
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text="Type:").grid(row=0, column=0)
        self.type_var = tk.StringVar(value="Expense")
        type_menu = ttk.Combobox(entry_frame, textvariable=self.type_var, values=["Income", "Expense"], width=15, state='readonly')
        type_menu.grid(row=0, column=1, padx=5)

        tk.Label(entry_frame, text="Amount:").grid(row=0, column=2)
        self.amount_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.amount_var, width=15).grid(row=0, column=3, padx=5)

        tk.Label(entry_frame, text="Description:").grid(row=1, column=0)
        self.desc_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, columnspan=3, pady=5)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Transaction", command=self.add_transaction).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Show Transactions", command=self.show_transactions).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Calculate Balance", command=self.calculate_balance).grid(row=0, column=2, padx=10)
        #Adding New Button[Undo ^]


        tk.Button(button_frame, text="Reset All", command=self.reset_all).grid(row=0, column=3, padx=10)
        #Adding New Button[REST ^]

        # Treeview for table
        self.tree = ttk.Treeview(self.window, columns=("Date", "Type", "Amount", "Description"), show='headings')
        for col in ("Date", "Type", "Amount", "Description"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor='center')
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def add_transaction(self):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trans_type = self.type_var.get()
        amount = self.amount_var.get()
        desc = self.desc_var.get()

        if not amount.strip().isdigit():
            messagebox.showerror("Error", "Amount must be a number.")
            return

        with open(FILE_NAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, trans_type, amount, desc])
        messagebox.showinfo("Success", "Transaction added successfully.")
        self.amount_var.set("")
        self.desc_var.set("")

    def show_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        with open(FILE_NAME, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.tree.insert('', tk.END, values=(row['Date'], row['Type'], row['Amount'], row['Description']))

    def calculate_balance(self):
        income = 0
        expense = 0

        with open(FILE_NAME, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                amount = float(row['Amount'])
                if row['Type'] == 'Income':
                    income += amount
                elif row['Type'] == 'Expense':
                    expense += amount

        balance = income - expense
        messagebox.showinfo("Balance", f"Total Income: ₹{income:.2f}\nTotal Expense: ₹{expense:.2f}\nBalance: ₹{balance:.2f}")
    
    #Adding a Method[REST v]
    def reset_all(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all transactions?")
        if confirm:
            with open(FILE_NAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Type', 'Amount', 'Description'])

        for item in self.tree.get_children():
            self.tree.delete(item)

        messagebox.showinfo("Reset Complete", "All transactions have been deleted.")


# Run the App
if __name__ == "__main__":
    window = tk.Tk()
    app = ExpenseTracker(window)
    window.mainloop()
