import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import numpy as np

@st.cache_data
def prepare_dataset(df_raw, map_col):
    df = df_raw.rename(columns=map_col)
    return df

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("E-Commerce Sales Analytics Dashboard")
st.caption("Automated business insights and forecasting")

tab1, tab2, tab3 = st.tabs(["Overview", "Inventory", "Forecasting"], width="stretch")

st.markdown("""
    <style>
            .main { background-color: #0f1117;}
            .metric-card { border-radius: 12px; padding: 20px;}
    </style>
""", unsafe_allow_html=True)

try:
    from src.data_loader import load_csv
    from src.cleaning import cleaning
    from src.kpis import (
        calculate_revenue_profit,
        calculate_growth,
        calculate_traffic,
        calculate_cac,
        calculate_best_seller  
    )
    from src.inventory import (
        daily_sales,
        inventory_level,
        stock_status
    )
    from src.forecasting import forecast
    from helpers import INCLUDE_NEGATIVE_AMOUNTS, TIME_GRAIN
    FUNCTIONS_AVAILABLE=True
except:
    FUNCTIONS_AVAILABLE=False
    st.warning("Could not import project functions. Make sure this file is in the project root.")

with st.sidebar:
    st.header("Settings")

    uploaded_file = st.file_uploader("Upload Sales File", type=["csv"], help="Upload your  sales file")
    inventory_file = st.file_uploader("Upload Inventory File (Optional)", type=['csv'])
    marketing_file = st.file_uploader("Upload Marketing File (Optional)", type=['csv'])
    
    if uploaded_file is not None and FUNCTIONS_AVAILABLE:
        try:
            temp_path = Path("temp_upload.csv")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            if "raw_df" not in st.session_state:
                st.session_state.raw_df = load_csv(temp_path)
            
            df_raw = st.session_state.raw_df
            columns = df_raw.columns.tolist()
            st.subheader("Map your columns")
            col_date = st.selectbox("Date column", columns)
            col_product = st.selectbox("Product name column", columns)
            col_customer = st.selectbox("Customer ID column", columns)
            col_quantity = st.selectbox("Quantity column", columns)
            col_price = st.selectbox("Unit Price column", columns)
            col_unit_cost = st.selectbox("Unit cost column", options=["None"] + columns, index=0)
            col_traffic = st.selectbox("Traffic source column",options=['None'] + columns, index=0)
            col_inventory = st.selectbox("Inventory column", options= ["None"] + columns, index=0)
            col_marketing = st.selectbox("Marketing spend column", options= ["None"] + columns, index=0)
            

            revenue_mode = st.radio(
                "Revenue Source",
                ["Use existing revenue column", "Calculate revenue (Quantity x Unit Price)"]
            )

            if revenue_mode == "Use existing revenue column":
                col_revenue = st.selectbox("Revenue column", columns)
            else:
                col_revenue = None

            # else:
            #     qty = st.selectbox("Quantity column", columns)
            #     up = st.selectbox("Unit Price column", columns)

            TIME_GRAIN = st.radio(
                "Time Grain",
                options=['D', 'W', 'M', 'Y', 'H', 'MIN', 'S'],
                format_func= lambda x: {'D':'Daily', 'W':'Weekly', 'M':'Monthly', 'Y':'Yearly', 'H':'Hourly', 'MIN':'Every Minute', 'S':'Every Second'}[x],
                index=2,
                help="This sets the Time Grain configuration"

            )

            INCLUDE_NEGATIVE_AMOUNTS = st.toggle("Include returns (negative quantity)", value=False)

            map_col = {
                col_date : 'date',
                col_product : 'product',
                col_customer : 'customer_id',
                col_quantity : 'quantity',
                col_price : 'unit_price'

            }
            if col_traffic!= 'None':
                map_col[col_traffic] = 'traffic_source'

            if col_revenue is not None:
                map_col[col_revenue] = 'revenue'
            
            if col_unit_cost != 'None':
                map_col[col_unit_cost] = 'unit_cost'
        

        except Exception as e:
            st.error(f"Error processing file : {str(e)}")
            st.exception(e)

            if Path("temp_upload.csv").exists():
                Path("temp_upload.csv").unlink()

    elif not FUNCTIONS_AVAILABLE:
        st.error("Cannot import project functions. Please ensure:")
        st.code("""
1. This file is in your project root directory
2. The 'src' folder is in the same directory
3. All required modules are installed
""")
        
    else:
        st.info("Please upload a CSV file to get started")


# data pipeline


if uploaded_file is not None and FUNCTIONS_AVAILABLE:
    if st.button("Generate Report"):
            st.session_state['run_report'] = True
            st.session_state['df_ready'] = True
    if st.session_state.get('run_report'):
        df = prepare_dataset(df_raw, map_col)
        
        if col_revenue is None:
            df['revenue'] = df['quantity'] * df['unit_price']

        
        df['date'] = pd.to_datetime(df['date'])
        df = cleaning(df)
        
        if col_inventory != 'None':
            df['inventory'] = df[col_inventory]
        elif inventory_file != None:
            df_inv = load_csv(inventory_file)
            inv_columns = df_inv.columns.tolist()
            inv_product = st.selectbox("Inventory product column", inv_columns)
            inv_stock = st.selectbox("Inventory stock column", inv_columns)
            df_inv = df_inv.rename(columns={
                inv_product: 'product',
                inv_stock: 'inventory'
            })
            df = df.merge(df_inv, on='product', how="left")
            
        if col_marketing != 'None':
            df['marketing_spend'] = df[col_marketing]
        elif marketing_file != None:
            df_mark = load_csv(marketing_file)
            mark_columns = df_mark.columns.tolist()
            mark_date = st.selectbox("Marketing spend date column", mark_columns)
            mark_spend = st.selectbox("Marketing spend column", mark_columns)
            df_mark = df_mark.rename(columns={
                mark_date:'date',
                mark_spend: 'marketing_spend'
            })
            df = df.merge(df_mark, on='date', how="left")

        st.session_state['df_final'] = df
elif not FUNCTIONS_AVAILABLE:
    st.error("Cannot import project functions. Please ensure:")
    st.code("""
1. This file is in your project root directory
2. The 'src' folder is in the same directory
3. All required modules are installed
""")
    
else:
    st.info("Please upload a CSV file to get started")

# Overview tab
with tab1:
        
        if st.session_state.get('run_report'):
            with st.spinner("Processing data..."):
                df = st.session_state.get('df_final')
                if df is None:
                    st.warning("Dataset not processed yet.")
                    st.stop()
                df_revenue = calculate_revenue_profit(df, TIME_GRAIN, INCLUDE_NEGATIVE_AMOUNTS)
                df_growth = calculate_growth(df)
                df_traffic = calculate_traffic(df)
                df_best_qty, df_best_rev = calculate_best_seller(df)
                df_cac = calculate_cac(df) if 'marketing_spend' in df.columns else None

                total_revenue = df['revenue'].sum()
                total_profit = df_revenue['profit'].sum()
                best_product = df_best_rev.iloc[0]['product']
                if 'traffic_source' in df.columns:
                    top_traffic = df_traffic.iloc[0]['traffic_source']
                else:
                    top_traffic = np.nan

                if df_cac is not None:
                    latest_cac = df_cac['cac'].iloc[-1]
                else:
                    latest_cac = np.nan

                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Revenue", f"${total_revenue:,.0f}")
                col2.metric("Profit", f"${total_profit:,.0f}")
                col3.metric("Best Seller", best_product)
                col4.metric("Top Traffic", top_traffic)
                col5.metric("Customer Acquisition Cost", f"${latest_cac:,.2f}")

                fig_revenue = px.line(
                    df_revenue,
                    x='date',
                    y='revenue',
                    title="Revenue Over Time"
                )
                
                st.plotly_chart(fig_revenue, use_container_width=True)

                if 'traffic_source' in df.columns:
                    fig_traffic = px.bar(
                        df_traffic,
                        x='traffic_source',
                        y='percentage',
                        title="Traffic Source Distribution"
                    )

                    st.plotly_chart(fig_traffic, use_container_width=True)

                fig_bestseller = px.bar(
                    df_best_rev.head(10),
                    x='product',
                    y='revenue',
                    title="Top Selling Products"
                )

                st.plotly_chart(fig_bestseller, use_container_width=True)

                if 'marketing_spend' in df.columns:

                    marketing_df = (
                        df
                        .set_index("date")
                        .resample(TIME_GRAIN)
                        .agg({
                            "revenue": "sum",
                            "marketing_spend": "sum"
                        })
                        .reset_index()
                    )

                    fig_marketing = px.line(
                        marketing_df,
                        x="date",
                        y=["revenue", "marketing_spend"],
                        title="Revenue vs Marketing Spend"
                    )

                    st.plotly_chart(fig_marketing, use_container_width=True)


                    total_marketing = df['marketing_spend'].sum()

                    if total_marketing > 0:
                        roas = total_revenue / total_marketing
                        st.metric("Return on Ad Spend (ROAS)", f"{roas:.2f}x")



# Inventory tab
with tab2:
    if st.session_state.get('run_report'):
        with st.spinner('Processing data...'):
            df = st.session_state.get('df_final')
            if df is not None and 'inventory' in df.columns and st.session_state.get("df_ready"):
                inv_level = inventory_level(df)
                daily_sales = daily_sales(df)

                inventory_df = inventory_level.merge(daily_sales, on='product')

                inventory_df['days_until_stockout'] = (
                    inventory_df['inventory'] / inventory_df['avg_daily_sales']
                )
                inventory_df['status'] = inventory_df['days_until_stockout'].apply(stock_status)

                st.dataframe(inventory_df)

                fig_inventory = px.bar(
                    inventory_df.sort_values('days_until_stockout'),
                    x='product',
                    y='days_until_stockout',
                    color='status',
                    title='Inventory Health (Days Until Stockout)'
                )
                st.plotly_chart(fig_inventory, use_container_width=True)

                low_stock = (inventory_df['days_until_stockout'] < 30).count()
                st.metric('Products Needing Reorder', low_stock)


# Forecasting tab
with tab3:
    if st.session_state.get('run_report'):
        with st.spinner('Processing data...'):
            df = st.session_state.get('df_final')
            if df is not None and st.session_state.get("df_ready"):
                st.subheader('Forecast Settings')
                col1, col2 = st.columns(2)

                with col1:
                    horizon = st.slider(
                        "Forecast Horizon",
                        min_value=1,
                        max_value=12,
                        value=3,
                        help="Number of future periods to forecast"
                    )

                with col2:
                    forecast_metric = st.selectbox(
                        "Metric to Forecast",
                        ['revenue'],
                        help="Currently forecasting revenue based on historical trend"
                    )

                forecast_df = forecast(df, horizon)

                fig_forecast = px.line(
                    forecast_df,
                    x='date',
                    y=['actual_revenue', 'forecast_revenue'],
                    title='Revenue Forecast'
                )

                st.plotly_chart(fig_forecast, use_container_width=True)

                st.subheader('Forecasted Revenue')

                future_only = forecast_df[forecast_df['actual_revenue'].isna()].drop(columns="actual_revenue")
                
                st.dataframe(future_only)

                last_actual= forecast_df['actual_revenue'].dropna().iloc[-1]
                next_forecast = future_only['forecast_revenue'].iloc[0]

                growth = (next_forecast - last_actual) / last_actual * 100
                st.metric("Expected Next Period Growth", f'{growth:.2f}%')

