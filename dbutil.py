import os
import psycopg2
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime
from utils.formatters import format_date_str

# --- Database Connection ---
@st.cache_resource
def get_connection_engine():
    #conn = psycopg2.connect(os.environ["SUPABASE_CONN_STRING"])
    conn_str = os.environ["SUPABASE_CONN_STRING"]
    engine = create_engine(conn_str)
    return engine

def get_connection():
    conn = psycopg2.connect(os.environ["SUPABASE_CONN_STRING"])
    return conn
    
# --- Helper Functions ---
def format_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") if d else ""

def execute_query(query, params=None):
    """
    Executes a SQL query with optional parameters.
    Opens a new connection and cursor for each call,
    commits if it's a modifying query, and closes resources.

    :param query: SQL query string with placeholders (%s)
    :param params: Tuple or list of parameters to pass with query
    """
    engine = get_connection_engine()        # Your method to get raw DB connection (e.g. psycopg2)
    raw_conn = engine.raw_connection()
    cur = raw_conn.cursor()
    try:
        cur.execute(query, params)
        # Commit only if the query modifies data
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER")):
            raw_conn.commit()
    except Exception as e:
        raw_conn.rollback()
        raise e
    finally:
        cur.close()
        raw_conn.close()

# --- Expense ---
def add_expense(date, category, amount, comment):
    execute_query(
        "INSERT INTO expenses (date, category, amount, comment) VALUES (%s,%s,%s,%s)",
        (date, category, amount, comment)
    )

def get_expenses():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
    if not df.empty:
        df["date"] = df["date"].apply(lambda d: format_date_str(d))
    return df

def save_expenses(df):
    execute_query("DELETE FROM expenses")
    for _, row in df.iterrows():
        execute_query(
            "INSERT INTO expenses (expense_id, date, category, amount, comment) VALUES (%s,%s,%s,%s,%s)",
            (row["expense_id"], row["date"], row["category"], row["amount"], row["comment"])
        )

# --- Income ---
def add_income(date, customer, amount, payment_method, comment):
    execute_query(
        "INSERT INTO income (date, customer, amount, payment_method, comment) VALUES (%s,%s,%s,%s,%s)",
        (date, customer, amount, payment_method, comment)
    )

def get_income():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM income ORDER BY date DESC", conn)
    if not df.empty:
        df["date"] = df["date"].apply(lambda d: format_date_str(d))
    return df

def save_income(df):
    execute_query("DELETE FROM income")
    for _, row in df.iterrows():
        execute_query(
            "INSERT INTO income (order_id, date, customer, amount, payment_method, comment) VALUES (%s,%s,%s,%s,%s,%s)",
            (row["order_id"], row["date"], row["customer"], row["amount"], row["payment_method"], row["comment"])
        )

# --- Orders ---
def add_order(delivery_date, customer, item, price, advance, description):
    pending = price - advance
    execute_query(
        """INSERT INTO orders (delivery_date, customer, item, price, advance, pending_balance, description, delivered)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (delivery_date, customer, item, price, advance, pending, description, False)
    )

def get_orders():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM orders ORDER BY delivery_date DESC", conn)
    if not df.empty:
        df["delivery_date"] = pd.to_datetime(df["delivery_date"]).dt.strftime("%d-%m-%Y")
    return df

def mark_order_delivered(order_id):
    execute_query("UPDATE orders SET delivered=True WHERE order_id=%s", (int(order_id),))

def move_order_to_income(order_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM orders WHERE order_id=%s", conn, params=(int(order_id),))
    if df.empty:
        print("No order found with that ID " + str(order_id))
        return
    
    order = df.iloc[0]
    try:
        execute_query(
            "INSERT INTO income (order_id, date, customer, amount, payment_method, comment) VALUES (%s,%s,%s,%s,%s,%s)",
            (
                int(order["order_id"]),
                order["delivery_date"],
                order["customer"],
                order["price"],
                "UPI",
                order["description"],
            ),
        )
        print("Insert into income succeeded")
    except Exception as e:
        print(f"Insert into income failed: {e}")
        raise

    execute_query("DELETE FROM orders WHERE order_id=%s", (int(order_id),))

def update_order(order_id, delivery_date, customer, item, price, advance, description):
    pending = price - advance
    execute_query(
        """UPDATE orders
           SET delivery_date=%s, customer=%s, item=%s, price=%s, advance=%s, pending_balance=%s, description=%s
           WHERE order_id=%s""",
        (delivery_date, customer, item, price, advance, pending, description, int(order_id))
    )

def cancel_order(order_id):
    execute_query("DELETE FROM orders WHERE order_id=%s", (int(order_id),))
