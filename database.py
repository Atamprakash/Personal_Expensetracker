import mysql.connector                            #Standard package/module
from tkinter import messagebox
import pandas as pd
from tkinter import filedialog
from config import DB_CONFIG                      #Config file, from that variable= DB_CONFIG

def connect_db():                                  #Creating a database connecting Func
    return mysql.connector.connect(**DB_CONFIG)    #Unpacking the DB_CONFIG by **

def insert_transaction(date, trans_type, amount, description, category):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, type, amount, description, category)
        VALUES (%s, %s, %s, %s, %s)
    """, (date, trans_type, amount, description, category))
    conn.commit()
    conn.close()

def fetch_all_transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, type, amount, description, category FROM transactions ORDER BY date DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_income_expense():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT type, amount FROM transactions")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_all_transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

def insert_csv():
    try:
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Handle NULL or missing values
        df['Description'] = df['Description'].fillna("")
        df['Category'] = df['Category'].fillna("Other")

        # Parse date flexibly
        try:
            df['date'] = pd.to_datetime(df['Date'], infer_datetime_format=True, errors='raise')
            df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as date_err:
            messagebox.showerror("Date Error", f"Failed to parse date column. Error: {date_err}")
            return

        conn = connect_db()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO transactions (date, type, amount, description, category)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row['date'],
                row['type'],
                row['amount'],
                row['Description'],
                row['Category']
            ))

        conn.commit()
        messagebox.showinfo("Success", "CSV data inserted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to insert CSV: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def delete_latest_transaction():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # First, retrieve the ID of the latest transaction
        cursor.execute("SELECT id FROM transactions ORDER BY date DESC LIMIT 1")
        latest_transaction = cursor.fetchone()  # Fetch the latest transaction

        if latest_transaction:  # If a transaction exists
            latest_transaction_id = latest_transaction[0]
            # Now, delete the transaction with that ID
            cursor.execute("DELETE FROM transactions WHERE id = %s", (latest_transaction_id,))
            conn.commit()
            messagebox.showinfo("Success", "Most recent transaction removed.")
        else:
            messagebox.showwarning("Warning", "No transactions found to undo.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("Error", "Failed to undo transaction.")
    finally:
        conn.close()


