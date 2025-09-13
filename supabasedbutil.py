import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
from utils.formatters import format_date_str

# --- Supabase Connection ---
@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]  # use Service Role for full CRUD
    return create_client(url, key)

supabase = get_supabase_client()

# --- Helper Functions ---
def format_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") if d else ""


# --- Expenses ---
def add_expense(date, category, amount, comment):
    supabase.table("expenses").insert({
        "date": date,
        "category": category,
        "amount": amount,
        "comment": comment
    }).execute()

def get_expenses():
    res = supabase.table("expenses").select("*").order("date", desc=True).execute()
    df = pd.DataFrame(res.data)
    return df

def save_expenses(df):
    allowed_columns = ["expense_id", "date", "category", "amount", "comment"]
    df = df[allowed_columns]
    data = df.to_dict(orient="records")
    for row in data:
        expense_id = row["expense_id"]
        supabase.table("expenses").update(row).eq("expense_id", expense_id).execute()

# --- Income ---
def add_income(date, customer, amount, payment_method, comment):
    supabase.table("income").insert({
        "date": date,
        "customer": customer,
        "amount": amount,
        "payment_method": payment_method,
        "comment": comment
    }).execute()
"""
def get_income():
    res = supabase.table("income").select("*").order("date", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df["date"] = df["date"].apply(lambda d: format_date_str(d))
    return df
"""
def get_income():
    res = supabase.table("income").select("*").order("date", desc=True).execute()
    df = pd.DataFrame(res.data)
    return df
    
def save_income(df):
    allowed_columns = ["order_id", "date", "customer", "amount", "payment_method", "comment"]
    df = df[allowed_columns]
    data = df.to_dict(orient="records")
    for row in data:
        order_id = row["order_id"]
        supabase.table("income").update(row).eq("order_id", order_id).execute()

# --- Orders ---
def add_order(delivery_date, customer, item, price, advance, description):
    pending = price - advance
   
    supabase.table("orders").insert({
        "delivery_date": delivery_date   ,
        "customer": customer,
        "item": item,
        "price": price,
        "advance": advance,
        "pending_balance": pending,
        "description": description,
        "delivered": False
    }).execute()

def get_orders():
    res = supabase.table("orders").select("*").order("delivery_date", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df["delivery_date"] = pd.to_datetime(df["delivery_date"]).dt.strftime("%d-%m-%Y")
    return df

def mark_order_delivered(order_id):
    supabase.table("orders").update({"delivered": True}).eq("order_id", int(order_id)).execute()

def move_order_to_income(order_id):
    res = supabase.table("orders").select("*").eq("order_id", int(order_id)).execute()
    if not res.data:
        print("No order found with that ID", order_id)
        return
    
    order = res.data[0]
    try:
        supabase.table("income").insert({
            "order_id": order["order_id"],
            "date": order["delivery_date"],
            "customer": order["customer"],
            "amount": order["price"],
            "payment_method": "UPI",
            "comment": order["description"]
        }).execute()
        print("Insert into income succeeded")
    except Exception as e:
        print(f"Insert into income failed: {e}")
        raise
    
    supabase.table("orders").delete().eq("order_id", int(order_id)).execute()

def update_order(order_id, delivery_date, customer, item, price, advance, description):
    pending = price - advance
    supabase.table("orders").update({
        "delivery_date": delivery_date,
        "customer": customer,
        "item": item,
        "price": price,
        "advance": advance,
        "pending_balance": pending,
        "description": description
    }).eq("order_id", int(order_id)).execute()

def cancel_order(order_id):
    supabase.table("orders").delete().eq("order_id", int(order_id)).execute()
