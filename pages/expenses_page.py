import streamlit as st
from datetime import date
from db import add_expense, get_expenses, save_expenses
from utils.aggrid_utils import editable_grid

def expenses_page():
    st.title("Add Expense")

    with st.form("expense_form"):
        e_date = st.date_input("Date", date.today())
        e_category = st.text_input("Category")
        e_amount_str = st.text_input("Amount")
        e_comment = st.text_area("Comment")
        if st.form_submit_button("Add Expense"):
            try:
                e_amount = float(e_amount_str)
                add_expense(str(e_date), e_category, e_amount, e_comment)
                st.success("Expense added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")

    st.subheader("Edit/Delete Expenses")
    df_exp = get_expenses()
    editable_grid(df_exp, save_expenses)
