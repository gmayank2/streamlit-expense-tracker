import streamlit as st
from datetime import date
from utils.formatters import parse_date_str
from supabasedbutil import add_order, get_orders, mark_order_delivered, move_order_to_income, update_order, cancel_order

def orders_page():
    st.title("Orders")

    if "editing_order" not in st.session_state:
        st.session_state["editing_order"] = None

    df_orders = get_orders()

    if df_orders.empty:
        st.info("No orders found.")
    else:
        df_orders = df_orders.sort_values(by="delivery_date", ascending=True)

    order_labels = [
        f"#{row['order_id']} - **{row['delivery_date']}** - {row['customer']} - {row['item']}"
        for _, row in df_orders.iterrows()
    ]
    selected = st.radio("Select an order", order_labels, index=0 if order_labels else None)

    if selected:
        # Find selected order
        idx = order_labels.index(selected)
        row = df_orders.iloc[idx]

        st.subheader(f"Details for Order #{row['order_id']}")
        st.write(f"**Delivery Date:** {row['delivery_date']}")
        st.write(f"**Customer:** {row['customer']}")
        st.write(f"**Item:** {row['item']}")
        st.write(f"**Price:** ₹{row['price']} | **Advance:** ₹{row['advance']} | **Pending:** ₹{row['pending_balance']}")
        st.write(f"**Description:** {row['description']}")

        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("Deliver", key=f"d_{row['order_id']}"):
            mark_order_delivered(row["order_id"])
            st.success("Order delivered!")
        if c2.button("Paid", key=f"p_{row['order_id']}"):
            move_order_to_income(row["order_id"])
            st.success("Order moved to income!")
        if c3.button("Edit", key=f"e_{row['order_id']}"):
            st.session_state["editing_order"] = row
        if c4.button("Cancel", key=f"c_{row['order_id']}"):
            cancel_order(row["order_id"])
            st.success("Order cancelled!")

        # --- Edit form ---
        if st.session_state["editing_order"] is not None:
            row = st.session_state["editing_order"]
            st.subheader(f"Edit Order – {row['customer']}")
            with st.form("edit_form", clear_on_submit=True):
                e_date = st.date_input("Delivery Date", parse_date_str(row['delivery_date']))
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
                            update_order(row["order_id"], str(e_date), e_customer, e_item, e_price, e_advance, e_desc)
                            st.success("Order updated successfully!")
                            st.session_state["editing_order"] = None
                        except ValueError:
                            st.error("Please enter valid numbers for price and advance.")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state["editing_order"] = None

    # --- Add order form ---
    st.subheader("Add Order")
    with st.form("order_form"):
        o_date = st.date_input("Delivery Date", date.today())
        o_customer = st.text_input("Customer")
        o_item = st.text_input("Item")
        o_price_str = st.number_input("Price", min_value=0)
        o_advance_str = st.number_input("Advance", min_value=0)
        o_desc = st.text_area("Detail Description")
        if st.form_submit_button("Add Order"):
            try:
                o_price = float(o_price_str)
                o_advance = float(o_advance_str)
                add_order(o_date, o_customer, o_item, o_price, o_advance, o_desc)
                st.success("Order added successfully!")
            except ValueError:
                st.error("Please enter valid numbers for price and advance.")
