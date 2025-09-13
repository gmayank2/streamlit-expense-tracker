import streamlit as st
from datetime import date
from supabasedbutil import add_income, get_income, save_income
from utils.aggrid_utils import editable_grid
from st_aggrid import GridOptionsBuilder

def income_page():
    st.title("Completed Orders")

    df = get_income()
    selected_cols = ["order_id", "date", "customer", "amount","payment_method","comment"]
    if not df.empty:
        filtered_df = df[selected_cols]
        gb=get_grid_options_builder(filtered_df)
        editable_grid(filtered_df, save_income, gb, grid_key="income" )
    else:
        st.info("No income records found yet.")

def get_grid_options_builder(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
    gb.configure_default_column(editable=True)
    gb.configure_column("id", hide=True)
    gb.configure_column("order_id", editable=False)  # Make 'order_id' read-only
    gb.configure_selection("multiple", use_checkbox=False)
    gb.configure_grid_options(suppressRowClickSelection=True)
    #gb.configure_column("date", headerCheckboxSelection=True, headerCheckboxSelectionFilteredOnly=True, checkboxSelection=True)
    gb.configure_column("order_id", width=80)
    gb.configure_column("date", width=80)
    gb.configure_column("customer", width=120)
    gb.configure_column("amount", width=80)
    gb.configure_column("payment_method", width=80)
    gb.configure_column("comment", width=150)
    return gb
    
    """
    st.subheader("Add Completed Order")
    with st.form("income_form"):
        i_date = st.date_input("Date", date.today())
        #i_date_str = i_date.strftime("%Y-%m-%d")
        i_date_str = i_date.strftime("%d-%m-%Y") 
        i_customer = st.text_input("Customer")
        i_amount_str = st.text_input("Amount")
        i_payment = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Other"])
        i_comment = st.text_area("Comment")
        if st.form_submit_button("Add Income"):
            try:
                i_amount = float(i_amount_str)
                add_income(i_date, i_customer, i_amount, i_payment, i_comment)
                st.success("Income added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")
    """