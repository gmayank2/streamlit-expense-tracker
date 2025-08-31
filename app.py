import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ---------------- Page Config ----------------
st.set_page_config(page_title="Finance Tracker", layout="wide")

# ---------------- DB Setup ----------------
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    comment TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    customer TEXT,
    amount REAL,
    payment_method TEXT,
    comment TEXT
)""")
conn.commit()

# ---------------- Helper Functions ----------------
def add_expense(date, category, amount, comment):
    c.execute("INSERT INTO expenses (date, category, amount, comment) VALUES (?,?,?,?)",
              (date, category, amount, comment))
    conn.commit()

def add_income(date, customer, amount, payment_method, comment):
    c.execute("INSERT INTO income (date, customer, amount, payment_method, comment) VALUES (?,?,?,?,?)",
              (date, customer, amount, payment_method, comment))
    conn.commit()

def get_expenses():
    return pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)

def get_income():
    return pd.read_sql("SELECT * FROM income ORDER BY date DESC", conn)

def save_expenses(df):
    c.execute("DELETE FROM expenses")  # clear old
    for _, row in df.iterrows():
        c.execute("INSERT INTO expenses (id, date, category, amount, comment) VALUES (?,?,?,?,?)",
                  (row["id"], row["date"], row["category"], row["amount"], row["comment"]))
    conn.commit()

def save_income(df):
    c.execute("DELETE FROM income")
    for _, row in df.iterrows():
        c.execute("INSERT INTO income (id, date, customer, amount, payment_method, comment) VALUES (?,?,?,?,?,?)",
                  (row["id"], row["date"], row["customer"], row["amount"], row["payment_method"], row["comment"]))
    conn.commit()

# ---------------- UI Pages ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Expense", "Income", "Summary"])

if page == "Expense":
    st.title("Add Expense")
    with st.form("expense_form"):
        e_date = st.date_input("Date", date.today())
        e_category = st.text_input("Category")
        e_amount_str = st.text_input("Amount")
        e_comment = st.text_area("Comment")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            try:
                e_amount = float(e_amount_str)
                add_expense(str(e_date), e_category, e_amount, e_comment)
                st.success("Expense added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")

    st.subheader("Edit/Delete Expenses in Grid")
    df_exp = get_expenses()

    if not df_exp.empty:
        gb = GridOptionsBuilder.from_dataframe(df_exp)
        gb.configure_pagination()
        gb.configure_default_column(editable=True)
        gb.configure_selection("multiple", use_checkbox=True)  # for delete
        grid = AgGrid(
            df_exp,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True
        )
        updated_df = pd.DataFrame(grid["data"])
        selected_rows = grid["selected_rows"]

        # Save edited data
        if st.button("Save Changes"):
            save_expenses(updated_df)
            st.success("Expenses updated successfully!")

        # Delete selected rows
        if st.button("Delete Selected"):
            if selected_rows:
                ids_to_delete = [r["id"] for r in selected_rows]
                df_exp = df_exp[~df_exp["id"].isin(ids_to_delete)]
                save_expenses(df_exp)
                st.success("Selected expenses deleted successfully!")

elif page == "Income":
    st.title("Add Income")
    with st.form("income_form"):
        i_date = st.date_input("Date", date.today())
        i_customer = st.text_input("Customer")
        i_amount_str = st.text_input("Amount")
        i_payment = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Other"])
        i_comment = st.text_area("Comment")
        submitted = st.form_submit_button("Add Income")
        if submitted:
            try:
                i_amount = float(i_amount_str)
                add_income(str(i_date), i_customer, i_amount, i_payment, i_comment)
                st.success("Income added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")

    st.subheader("Edit/Delete Income in Grid")
    df_inc = get_income()

    if not df_inc.empty:
        gb = GridOptionsBuilder.from_dataframe(df_inc)
        gb.configure_pagination()
        gb.configure_default_column(editable=True)
        gb.configure_selection("multiple", use_checkbox=True)
        grid = AgGrid(
            df_inc,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True
        )
        updated_df = pd.DataFrame(grid["data"])
        selected_rows = grid["selected_rows"]

        # Save edited data
        if st.button("Save Changes"):
            save_income(updated_df)
            st.success("Income updated successfully!")

        # Delete selected rows
        if st.button("Delete Selected"):
            if selected_rows:
                ids_to_delete = [r["id"] for r in selected_rows]
                df_inc = df_inc[~df_inc["id"].isin(ids_to_delete)]
                save_income(df_inc)
                st.success("Selected income deleted successfully!")

elif page == "Summary":
    st.title("Monthly Summary")

    df_exp = get_expenses()
    df_inc = get_income()

    if not df_exp.empty:
        df_exp["date"] = pd.to_datetime(df_exp["date"])
        df_exp["Month"] = df_exp["date"].dt.to_period("M")
        exp_summary = df_exp.groupby("Month")["amount"].sum().reset_index()
        exp_summary.rename(columns={"amount": "Total Expense"}, inplace=True)
    else:
        exp_summary = pd.DataFrame(columns=["Month", "Total Expense"])

    if not df_inc.empty:
        df_inc["date"] = pd.to_datetime(df_inc["date"])
        df_inc["Month"] = df_inc["date"].dt.to_period("M")
        inc_summary = df_inc.groupby("Month")["amount"].sum().reset_index()
        inc_summary.rename(columns={"amount": "Total Income"}, inplace=True)
    else:
        inc_summary = pd.DataFrame(columns=["Month", "Total Income"])

    # Merge expense and income
    summary = pd.merge(exp_summary, inc_summary, on="Month", how="outer").fillna(0)
    summary["Net Savings"] = summary["Total Income"] - summary["Total Expense"]

    st.dataframe(summary, use_container_width=True)
