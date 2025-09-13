import streamlit as st
from datetime import datetime, date
import pandas as pd
from utils.formatters import parse_date_str
from supabasedbutil import add_order, get_orders, mark_order_delivered, move_order_to_income, update_order, cancel_order


# helper: safe iso string
def to_iso_string(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return str(val)


# helper: format a value for display as DD-MM-YYYY without changing stored value/type
def format_date_for_display(val):
    if pd.isna(val):
        return ""
    # If it's a pandas Timestamp or datetime
    if isinstance(val, (pd.Timestamp, datetime)):
        try:
            return pd.to_datetime(val).strftime('%d-%m-%Y')
        except Exception:
            return str(val)
    # If it's a date object
    if isinstance(val, date):
        try:
            return val.strftime('%d-%m-%Y')
        except Exception:
            return str(val)
    # Fallback: try to parse
    try:
        return pd.to_datetime(val).strftime('%d-%m-%Y')
    except Exception:
        return str(val)


def orders_page():

    if "editing_order" not in st.session_state:
        st.session_state["editing_order"] = None

    df_orders = get_orders()

    if df_orders.empty:
        st.info("No orders found.")
    else:

        # Ensure delivery_date column exists and convert it to python date objects for consistent comparisons
        if "delivery_date" in df_orders.columns:
            # Convert to datetime then to date (python.date) to match streamlit date_input outputs
            df_orders['delivery_date'] = pd.to_datetime(df_orders['delivery_date'], errors='coerce').dt.date
        else:
            # Keep behavior unchanged; just avoid crashing later
            st.error("delivery_date column not found in orders data.")

        # Now it's safe to sort by delivery_date (they are date objects or NaT/NaN converted to NaT->NaN)
        # For rows where conversion failed, pandas will have NaN; sort_values will put them at the end.
        df_orders = df_orders.sort_values(by="delivery_date", ascending=True)

        # Use python.date for today so comparisons with df (which are python.date) are consistent
        today = date.today()
        payment_pending = df_orders[df_orders['delivery_date'] < today]
        open_orders = df_orders[df_orders['delivery_date'] >= today]

        st.subheader("📌 Open Orders")
        if open_orders.empty:
            st.write("No open orders.")
        else:
            for _, row in open_orders.iterrows():
                d = format_date_for_display(row['delivery_date'])  # DD-MM-YYYY for display
                order_label = f"**{d}** – {row['customer']} – {row['item']} - #{row['order_id']}"
                if st.button(order_label, key=f"open_{row['order_id']}"):
                    st.session_state["selected_order"] = row

        st.subheader("📌 Payment Pending")
        if payment_pending.empty:
            st.write("No payment pending orders.")
        else:
            for _, row in payment_pending.iterrows():
                d = format_date_for_display(row['delivery_date'])
                order_label = f"**{d}** – {row['customer']} – {row['item']} - #{row['order_id']}"
                if st.button(order_label, key=f"pending_{row['order_id']}"):
                    st.session_state["selected_order"] = row

        if "selected_order" in st.session_state:
            row = st.session_state["selected_order"]
            st.subheader(f"Details for Order #{row['order_id']}")
            st.write(f"**Delivery Date:** {format_date_for_display(row['delivery_date'])}")
            st.write(f"**Customer:** {row['customer']}")
            st.write(f"**Item:** {row['item']}")
            st.write(f"**Price:** ₹{row['price']} | **Advance:** ₹{row['advance']} | **Pending:** ₹{row['pending_balance']}")
            st.write(f"**Description:** {row['description']}")

            c1, c2, c3, c4 = st.columns(4)
            if row.get("delivered", False):
                c1.button("Delivered", disabled=True)
            else:
                if c1.button("Deliver"):
                    mark_order_delivered(row["order_id"])
                    st.success("Order delivered!")
                    st.rerun()
            if c2.button("Paid"):
                move_order_to_income(row["order_id"])
                st.success("Order moved to income!")
                st.rerun()
            if c3.button("Edit"):
                st.session_state["editing_order"] = row
                st.rerun()
            if c4.button("Cancel"):
                cancel_order(row["order_id"])
                st.success("Order cancelled!")
                st.rerun()

            if st.session_state["editing_order"] is not None:
                row = st.session_state["editing_order"]
                st.subheader(f"Edit Order – {row['customer']}")
                with st.form("edit_form", clear_on_submit=True):
                    # Ensure default_date is a python.date
                    if isinstance(row.get('delivery_date'), date):
                        default_date = row.get('delivery_date')
                    else:
                        try:
                            default_date = pd.to_datetime(row.get('delivery_date')).date()
                        except Exception:
                            default_date = date.today()

                    e_date = st.date_input("Delivery Date", default_date)
                    e_customer = st.text_input("Customer", row['customer'])
                    e_item = st.text_input("Item", row['item'])
                    e_price_str = st.text_input("Price", str(row['price']))
                    e_advance_str = st.text_input("Advance", str(row['advance']))
                    e_desc = st.text_area("Description", row['description'])
                    col1, col2 = st.columns([1,1])
                    with col1:
                        if st.form_submit_button("Update Order"):
                            try:
                                e_price = float(e_price_str)
                                e_advance = float(e_advance_str)
                                # e_date from st.date_input is a python.date, so pass str(e_date) which yields ISO 'YYYY-MM-DD'
                                update_order(
                                    row["order_id"],
                                    e_date.isoformat(),
                                    e_customer,
                                    e_item,
                                    e_price,
                                    e_advance,
                                    e_desc
                                )
                                st.success("Order updated successfully!")
                                st.session_state["editing_order"] = None
                                st.rerun()
                            except ValueError:
                                st.error("Please enter valid numbers for price and advance.")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state["editing_order"] = None

    st.subheader("Add Order")

    with st.form("order_form", clear_on_submit=True):
        # st.date_input accepts datetime or date; using date.today() keeps it consistent
        o_date = st.date_input("Delivery Date", date.today(), key="o_date")
        o_customer = st.text_input("Customer", key="o_customer")
        o_item = st.text_input("Item", key="o_item")
        o_price_str = st.number_input("Price", min_value=0, key="o_price")
        o_advance_str = st.number_input("Advance", min_value=0, key="o_advance")
        o_desc = st.text_area("Detail Description", key="o_desc")

        if st.form_submit_button("Add Order"):
            try:
                o_price = float(o_price_str)
                o_advance = float(o_advance_str)
                # o_date is a python.date; str(o_date) yields ISO string 'YYYY-MM-DD' — do not change this type
                add_order(
                    o_date.isoformat(),
                    o_customer,
                    o_item,
                    o_price,
                    o_advance,
                    o_desc
                )
                st.success("Order added successfully!")
                for key in ["o_date", "o_customer", "o_item", "o_price", "o_advance", "o_desc"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            except ValueError:
                st.error("Please enter valid numbers for price and advance.")
