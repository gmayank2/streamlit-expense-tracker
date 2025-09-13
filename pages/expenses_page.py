import streamlit as st
from datetime import date
from supabasedbutil import add_expense, get_expenses, save_expenses
from utils.aggrid_utils import editable_grid
from st_aggrid import GridOptionsBuilder

def expenses_page():
    st.title("Add all expense")

    with st.form("expense_form"):
        e_date = st.date_input("Date", date.today())
        e_category = st.text_input("Category")
        #e_amount_str = st.text_input("Amount")
        e_amount_str = st.number_input("Amount", min_value=0)
        e_comment = st.text_area("Comment")
        if st.form_submit_button("Add Expense"):
            try:
                e_amount = float(e_amount_str)
                add_expense(str(e_date), e_category, e_amount, e_comment)
                st.success("Expense added successfully!")
            except ValueError:
                st.error("Please enter a valid number for amount.")

    st.subheader("Edit Expenses")
    selected_cols = ["expense_id", "date", "category", "amount","comment"]
    df_exp = get_expenses()
    if not df_exp.empty:
        filtered_df = df_exp[selected_cols]
        gb=get_grid_options_builder(filtered_df)
        editable_grid(filtered_df, save_expenses, gb, grid_key="expenses")
    else:
        st.info("No Expense records found yet.")


def get_grid_options_builder(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
    gb.configure_default_column(editable=True)
    gb.configure_column("id", hide=True)
    gb.configure_column("expense_id", editable=False)  # Make 'expense_id' read-only
    gb.configure_selection("multiple", use_checkbox=False)
    gb.configure_grid_options(suppressRowClickSelection=True)
    #gb.configure_column("date", headerCheckboxSelection=True, headerCheckboxSelectionFilteredOnly=True, checkboxSelection=True)
    gb.configure_column("expense_id", width=80)
    gb.configure_column("date", width=80)
    gb.configure_column("category", width=120)
    gb.configure_column("amount", width=80)
    gb.configure_column("comment", width=150)
    return gb