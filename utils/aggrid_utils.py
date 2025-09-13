from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import pandas as pd
import streamlit as st
from utils.formatters import format_date_str

def editable_grid(df, save_func, grid_options_builder, delete_enabled=False, grid_key="default_grid"):
    if df.empty:
        st.info("No records found.")
        return
    gb = grid_options_builder

    df["date"] = df["date"].apply(lambda d: format_date_str(d))


    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True
    )

    updated_df = pd.DataFrame(grid["data"])
    selected_rows = pd.DataFrame(grid["selected_rows"])

    if st.button("Save Changes", key=f"save_changes_{grid_key}"):
        updated_df['date'] = pd.to_datetime(updated_df['date'], format="%d-%m-%Y", errors="coerce").dt.date
        df.update(updated_df)
        df['date'] = df['date'].apply(lambda d: d.isoformat() if pd.notnull(d) else None)
        save_func(df)
        st.success("Changes saved successfully!")

    if delete_enabled and st.button("Delete Selected", key=f"delete_selected_{grid_key}"):
        if not selected_rows.empty:
            ids_to_delete = selected_rows["id"].tolist()
            df = df[~df["id"].isin(ids_to_delete)]
            save_func(df)
            st.success("Selected records deleted successfully!")
