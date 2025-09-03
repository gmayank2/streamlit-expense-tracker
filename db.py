import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, date
from utils.formatters import format_date_str

# --- Database Connection ---
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()

# --- Table Setup ---
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    comment TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS income (
    order_id INTEGER PRIMARY KEY,
    date TEXT,
    customer TEXT,
    amount REAL,
    payment_method TEXT,
    comment TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_date TEXT,
    customer TEXT,
    item TEXT,
    price REAL,
    advance REAL,
    pending_balance REAL,
    description TEXT,
    delivered INTEGER DEFAULT 0
)
""")

conn.commit()

# --- Helper Functions ---
def format_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") if d else ""

# --- Expense ---
def add_expense(date, category, amount, comment):
    c.execute("INSERT INTO expenses (date, category, amount, comment) VALUES (?,?,?,?)",
              (date, category, amount, comment))
    conn.commit()

def get_expenses():
    df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
    if not df.empty:
        df["date"] = df["date"].apply(lambda d: format_date_str(d))
    return df

def save_expenses(df):
    c.execute("DELETE FROM expenses")
    for _, row in df.iterrows():
        c.execute("INSERT INTO expenses (id, date, category, amount, comment) VALUES (?,?,?,?,?)",
                  (row["id"], row["date"], row["category"], row["amount"], row["comment"]))
    conn.commit()

# --- Income ---
def add_income(date, customer, amount, payment_method, comment):
    c.execute("INSERT INTO income (date, customer, amount, payment_method, comment) VALUES (?,?,?,?,?)",
              (date, customer, amount, payment_method, comment))
    conn.commit()

def get_income():
    df = pd.read_sql("SELECT * FROM income ORDER BY date DESC", conn)
    if not df.empty:
        df["date"] = df["date"].apply(lambda d: format_date_str(d))
    return df

def save_income(df):
    c.execute("DELETE FROM income")
    for _, row in df.iterrows():
        c.execute("INSERT INTO income (id, date, customer, amount, payment_method, comment) VALUES (?,?,?,?,?,?)",
                  (row["id"], row["date"], row["customer"], row["amount"], row["payment_method"], row["comment"]))
    conn.commit()

# --- Orders ---
def add_order(delivery_date, customer, item, price, advance, description):
    pending = price - advance
    c.execute("""INSERT INTO orders (delivery_date, customer, item, price, advance, pending_balance, description)
                 VALUES (?,?,?,?,?,?,?)""",
              (delivery_date, customer, item, price, advance, pending, description))
    conn.commit()

def get_orders():
    df = pd.read_sql("SELECT * FROM orders ORDER BY delivery_date DESC", conn)
    if not df.empty:
        df["delivery_date"] = pd.to_datetime(df["delivery_date"]).dt.strftime("%d-%m-%Y")
    return df

def mark_order_delivered(order_id):
    c.execute("UPDATE orders SET delivered=1 WHERE order_id=?", (int(order_id),))
    conn.commit()

def move_order_to_income(order_id):
    df = pd.read_sql("SELECT * FROM orders WHERE order_id=?", conn, params=(int(order_id),))
    if df.empty:
        print("No order found with that ID " + str(order_id) )
        return
    order = df.iloc[0]  # first row as Series
    # Use fields that exist in income table: date, customer, amount, payment_method, comment
    
    try:
        c.execute(
            "INSERT INTO income (order_id, date, customer, amount, payment_method, comment) VALUES (?, ?, ?, ?, ?, ?)",
            (
                int(order["order_id"]),
                order["delivery_date"],
                order["customer"],
                order["price"],
                "UPI",  # default or real payment_method if available
                order["description"]  # will be stored as 'comment'
            )
        )
        if c.rowcount == 1:
            print("Insert into income succeeded")
        else:
            print(f"Insert into income affected unexpected number of rows: {c.rowcount}")
    except Exception as e:
        print(f"Insert into income failed: {e}")
        raise  # re-raise or handle as needed
    
    c.execute("DELETE FROM orders WHERE order_id=?", (int(order_id),))
    conn.commit()

def update_order(order_id, delivery_date, customer, item, price, advance, description):
    pending = price - advance
    c.execute("""UPDATE orders
                 SET delivery_date=?, customer=?, item=?, price=?, advance=?, pending_balance=?, description=?
                 WHERE order_id=?""",
              (delivery_date, customer, item, price, advance, pending, description, int(order_id)))
    conn.commit()

def cancel_order (order_id):
    c.execute("DELETE FROM orders WHERE order_id=?", (int(order_id),))
    conn.commit()