import streamlit as st
from datetime import date
from db import add_order, get_orders, mark_order_delivered, move_order_to_income, update_order

def orders_page():
    st.title("Orders")

    # CSS for tiles
    st.markdown("""
        <style>
        .order-card {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            margin-bottom: 10px;
            background-color: #f9f9f9;
        }
        .order-field { margin: 2px 0; font-size: 13px; }
        .order-date { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
        </style>
    """, unsafe_allow_html=True)

    if "editing_order" not in st.session_state:
        st.session_state["editing_order"] = None

    st.subheader("Order List")
    df_orders = get_orders().sort_values(by="delivery_date", ascending=True)

    if not df_orders.empty:
        for i in range(0, len(df_orders), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_orders):
                    row = df_orders.iloc[i + j]
                    with cols[j]:
                        with st.container():
                            st.markdown(
                                f"""
                                <div class='order-card'>
                                    <div class='order-date'>{row['delivery_date']}</div>
                                    <div class='order-field'>Order Id: {row['order_id']}</div>
                                    <div class='order-field'>Customer: {row['customer']}</div>
                                    <div class='order-field'>Item: {row['item']}</div>
                                    <div class='order-field'>Price: {row['price']}</div>
                                    <div class='order-field'>Advance: {row['advance']}</div>
                                    <div class='order-field'>Pending: {row['pending_balance']}</div>
                                    <div class='order-field'>Description: {row['description']}</div>
                                </div>
                                """, unsafe_allow_html=True
                            )

                            c1, c2, c3 = st.columns(3)
                            with c1:
                                if row["delivered"] == 0:
                                    if st.button("Delivered", key=f"delivered_{row['order_id']}"):
                                        mark_order_delivered(row["order_id"])
                                        st.rerun()
                                else:
                                    st.button("Delivered", key=f"delivered_{row['order_id']}", disabled=True)
                            with c2:
                                if st.button("Fully Paid", key=f"paid_{row['order_id']}"):
                                    move_order_to_income(row["order_id"])
                                    st.success("Order moved to Income!")
                                    st.rerun()
                            with c3:
                                if st.button("Edit", key=f"edit_{row['order_id']}"):
                                    st.session_state["editing_order"] = row

    else:
        st.info("No orders found.")

    # 🔹 Show wide Edit form if one is selected
    if st.session_state["editing_order"] is not None:
        row = st.session_state["editing_order"]
        st.subheader(f"Edit Order – {row['customer']}")
        with st.form("edit_form", clear_on_submit=True):
            e_date = st.date_input("Delivery Date", date.today())
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
                        st.rerun()
                    except ValueError:
                        st.error("Please enter valid numbers for price and advance.")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state["editing_order"] = None
                    st.rerun()

    # 🔹 Add Order form at bottom
    st.subheader("Add Order")
    with st.form("order_form"):
        o_date = st.date_input("Delivery Date", date.today())
        o_customer = st.text_input("Customer")
        o_item = st.text_input("Item")
        o_price_str = st.text_input("Price")
        o_advance_str = st.text_input("Advance")
        o_desc = st.text_area("Detail Description")
        if st.form_submit_button("Add Order"):
            try:
                o_price = float(o_price_str)
                o_advance = float(o_advance_str)
                add_order(str(o_date), o_customer, o_item, o_price, o_advance, o_desc)
                st.success("Order added successfully!")
                st.rerun()
            except ValueError:
                st.error("Please enter valid numbers for price and advance.")

