import streamlit as st
from datetime import date
from dbutil import add_income, get_income, save_income
from utils.aggrid_utils import editable_grid

def income_page():
    st.title("Completed Orders")

    df = get_income()
    selected_cols = ["order_id", "date", "customer", "amount","payment_method","comment"]
    filtered_df = df[selected_cols]
    editable_grid(filtered_df, save_income, grid_key="income")

    st.subheader("Add Completed Order")
    with st.form("income_form"):
        i_date = st.date_input("Date", date.today())
        #i_date_str = st.text_input("Delivery Date", (date.today()).strftime("%d-%m-%Y"))
        i_customer = st.text_input("Customer")
        i_amount_str = st.text_input("Amount")
        i_payment = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Other"])
        i_comment = st.text_area("Comment")
        if st.form_submit_button("Add Income"):
            try:
                i_amount = float(i_amount_str)
                add_income(i_date_str, i_customer, i_amount, i_payment, i_comment)
                st.success("Income added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")
