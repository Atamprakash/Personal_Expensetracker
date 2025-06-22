import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

from analysis import (
    fetch_data,
    create_analysis_plot,
    embed_plot_into_tk
)

from database import (
    insert_transaction,
    fetch_all_transactions,
    fetch_income_expense,
    delete_all_transactions,
    delete_latest_transaction, # Import the undo function  
    insert_csv
)

from ml import (
    prepare_data,
    train_model,
    make_predictions,
    plot_forecast
)

from utils import export_to_csv


class ExpenseTracker:
    def __init__(self, window):
        self.window = window
        self.window.title("Personal Expense Tracker")
        self.window.geometry("1000x500")
        self.window.resizable(True, True)
        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.window)
        title_frame.pack(pady=(10, 5))
        title = tk.Label(title_frame, text="Expense Tracker", font=("Arial", 24, 'bold'))
        title.pack()

        # Input Form
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)

        # Row 1
        tk.Label(form_frame, text="Type:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.type_var = tk.StringVar(value="Expense")
        type_menu = ttk.Combobox(form_frame, textvariable=self.type_var, values=["Income", "Expense"], width=15, state='readonly')
        type_menu.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Amount:").grid(row=0, column=2, sticky='e', padx=5)
        self.amount_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.amount_var, width=15).grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Date:").grid(row=0, column=4, sticky='e', padx=5)
        self.date_entry = DateEntry(form_frame, width=18, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=5, padx=5)

        # Row 2
        tk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky='e', padx=5)
        self.desc_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        tk.Label(form_frame, text="Category:").grid(row=1, column=4, sticky='e', padx=5)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(form_frame, textvariable=self.category_var,
                                          values=['Home', 'Food', 'Transport', 'Bills', 'Income', 'Health', 'Socail',
                                                  'Shopping', 'Salary', 'Rental', 'Return', 'Education'], width=15)
        self.category_menu.grid(row=1, column=5, padx=5)
        self.category_var.set("")

        # Add Button
        # Row 3 - Add and Upload buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=(10, 5))

        tk.Button(button_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Upload CSV", command=self.upload_csv).pack(side=tk.LEFT, padx=5)


        # Action Buttons
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=5)
        for i, (label, cmd) in enumerate([
            ("Show Transactions", self.show_transactions),
            ("Calculate Balance", self.calculate_balance),
            ("Reset All", self.reset_all),
            ("Download Statement", self.download_statement),
            ("Undo", self.undo_transaction)  # Undo Button
        ]):
            tk.Button(action_frame, text=label, command=cmd).grid(row=0, column=i, padx=10)

        # Analytics Buttons
        analytics_frame = tk.Frame(self.window)
        analytics_frame.pack(pady=5)
        tk.Button(analytics_frame, text="Show Analysis", command=self.show_analysis).grid(row=0, column=0, padx=10)
        tk.Button(analytics_frame, text="Show Forecast", command=self.show_forecast).grid(row=0, column=1, padx=10)

        # Table
        self.tree = ttk.Treeview(self.window, columns=("Date", "Type", "Amount", "Description", "Category"), show='headings')
        for col in ("Date", "Type", "Amount", "Description", "Category"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def add_transaction(self):
        selected_date = self.date_entry.get()
        current_time = datetime.now().strftime("%H:%M:%S")
        date = f"{selected_date} {current_time}"

        trans_type = self.type_var.get()
        amount = self.amount_var.get()
        desc = self.desc_var.get()
        category = self.category_var.get()

        if not amount.strip().replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Amount must be a number.")
            return

        insert_transaction(date, trans_type, amount, desc, category)
        messagebox.showinfo("Success", "Transaction added successfully.")
        self.amount_var.set("")
        self.desc_var.set("")
        self.category_var.set("")

    def undo_transaction(self):
        # Undo the most recent transaction
        try:
            delete_latest_transaction()  # Call the delete function
            messagebox.showinfo("Success", "Most recent transaction removed.")
            self.show_transactions()  # Refresh the transaction table after undo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to undo transaction: {str(e)}")

    def show_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in fetch_all_transactions():
            self.tree.insert('', tk.END, values=row)

    def calculate_balance(self):
        income = expense = 0
        for t_type, amt in fetch_income_expense():
            if t_type == 'Income':
                income += float(amt)
            elif t_type == 'Expense':
                expense += float(amt)

        balance = income - expense
        messagebox.showinfo("Balance", f"Total Income: ₹{income:.2f}\nTotal Expense: ₹{expense:.2f}\nBalance: ₹{balance:.2f}")

    def reset_all(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all transactions?")
        if confirm:
            delete_all_transactions()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Reset Complete", "All transactions have been deleted.")

    def download_statement(self):
        data = fetch_all_transactions()
        headers = ["Date", "Type", "Amount", "Description", "Category"]
        export_to_csv(data, headers)

    def show_analysis(self):
        income, expense, income_totals, expense_totals = fetch_data()  # ✅ updated
        fig = create_analysis_plot(income, expense, income_totals, expense_totals)
        analysis_window = tk.Toplevel(self.window)
        analysis_window.title("Expense Analysis")
        analysis_window.geometry("1000x650")
        embed_plot_into_tk(fig, analysis_window)


    def show_forecast(self):
        df = prepare_data()
        model = train_model(df)
        forecast = make_predictions(model)
        plot_forecast(model, forecast)
    
    def upload_csv(self):
        try:
            insert_csv()  # Refresh the table after upload
        except Exception as e:
            messagebox.showerror("Error", f"CSV upload failed: {str(e)}")



def run_app():
    window = tk.Tk()
    app = ExpenseTracker(window)
    window.mainloop()
