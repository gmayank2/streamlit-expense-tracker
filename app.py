import streamlit as st
import logging
import os
import pytz
import socket

from pages.expenses_page import expenses_page
from pages.income_page import income_page
from pages.orders_page import orders_page
from pages.summary_page import summary_page
from datetime import datetime

#os.environ['SUPABASE_CONN_STRING'] = "postgresql://postgres:VibrantCakes12@db.tmmyrqbojigzfzykjtyo.supabase.co:5432/postgres?sslmode=require"

@st.cache_resource
def get_deploy_time():
    return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

st.sidebar.markdown(f"**Last deployed:** {get_deploy_time()}")
st.set_page_config(page_title="Finance Tracker", layout="wide")

tabs = st.tabs(["Orders", "Completed Orders", "Expenses", "Summary"])

with tabs[0]:
    orders_page()

with tabs[1]:
    income_page()

with tabs[2]:
    expenses_page()

with tabs[3]:
    summary_page()