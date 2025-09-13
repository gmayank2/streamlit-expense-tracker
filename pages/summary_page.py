import streamlit as st
import pandas as pd
from supabasedbutil import get_expenses, get_income
from utils.formatters import parse_date_str

def summary_page():
    st.title("Monthly Summary")

    df_exp = get_expenses()
    df_inc = get_income()

    if not df_exp.empty:
        df_exp["date"] = pd.to_datetime(df_exp["date"], format="%Y-%m-%d")
        df_exp["Month"] = df_exp["date"].dt.to_period("M")
        exp_summary = df_exp.groupby("Month")["amount"].sum().reset_index()
        exp_summary.rename(columns={"amount": "Total Expense"}, inplace=True)
    else:
        exp_summary = pd.DataFrame(columns=["Month", "Total Expense"])

    if not df_inc.empty:
        df_inc["date"] = pd.to_datetime(df_inc["date"], format="%Y-%m-%d")
        df_inc["Month"] = df_inc["date"].dt.to_period("M")
        inc_summary = df_inc.groupby("Month")["amount"].sum().reset_index()
        inc_summary.rename(columns={"amount": "Total Income"}, inplace=True)
    else:
        inc_summary = pd.DataFrame(columns=["Month", "Total Income"])

    summary = pd.merge(exp_summary, inc_summary, on="Month", how="outer").fillna(0)
    summary["Net Savings"] = summary["Total Income"] - summary["Total Expense"]

    st.dataframe(summary, width='stretch')
