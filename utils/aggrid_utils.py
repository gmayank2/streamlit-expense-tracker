from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import pandas as pd
import streamlit as st

def editable_grid(df, save_func, delete_enabled=False, grid_key="default_grid"):
    if df.empty:
        st.info("No records found.")
        return

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
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

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True
    )

    updated_df = pd.DataFrame(grid["data"])
    selected_rows = pd.DataFrame(grid["selected_rows"])

    if st.button("Save Changes", key=f"save_changes_{grid_key}"):
        df.update(updated_df)
        save_func(df)
        st.success("Changes saved successfully!")

    if delete_enabled and st.button("Delete Selected", key=f"delete_selected_{grid_key}"):
        if not selected_rows.empty:
            ids_to_delete = selected_rows["id"].tolist()
            df = df[~df["id"].isin(ids_to_delete)]
            save_func(df)
            st.success("Selected records deleted successfully!")
