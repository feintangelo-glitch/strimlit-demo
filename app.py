import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from generate_data import generate_sample_data

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Executive Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    /* Global Container Styling */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Custom KPI Metric Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 20px;
        color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: left;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
    }
    .text-positive { color: #10b981; }
    .text-negative { color: #ef4444; }
    .text-neutral { color: #3b82f6; }
    
    /* Tab headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background-color: rgba(255, 255, 255, 0.03);
    }
    </style>
""", unsafe_allow_html=True)


# --- DATA LOADING & CACHING ---
DATA_FILE = "sales_data.csv"

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        df = generate_sample_data(num_records=3500, file_path=file_path)
    else:
        df = pd.read_csv(file_path)
    
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df

df_raw = load_data(DATA_FILE)

# --- SIDEBAR FILTERS ---
st.sidebar.image("https://img.icons8.com/color/96/dashboard-layout.png", width=64)
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Filter sales performance data dynamically.")

# Date Range Filter
min_date = df_raw["Order_Date"].min().date()
max_date = df_raw["Order_Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

# Region Filter
all_regions = sorted(df_raw["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Regions",
    options=all_regions,
    default=all_regions
)

# Product Category Filter
all_categories = sorted(df_raw["Product_Category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_categories,
    default=all_categories
)

# Customer Segment Filter
all_segments = sorted(df_raw["Customer_Segment"].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segments",
    options=all_segments,
    default=all_segments
)

# Shipping Status Filter
all_statuses = sorted(df_raw["Shipping_Status"].unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Shipping Status",
    options=all_statuses,
    default=all_statuses
)

st.sidebar.markdown("---")

# Data Regeneration Trigger
with st.sidebar.expander("⚙️ Dataset Settings"):
    st.write("Regenerate synthetic dataset with a custom sample size.")
    num_samples = st.number_input("Number of Records", min_value=500, max_value=20000, value=3500, step=500)
    if st.button("🔄 Generate New Data"):
        generate_sample_data(num_records=int(num_samples), file_path=DATA_FILE)
        st.cache_data.clear()
        st.rerun()

# --- FILTERING DATAFRAME ---
mask = (
    (df_raw["Order_Date"].dt.date >= start_date) &
    (df_raw["Order_Date"].dt.date <= end_date) &
    (df_raw["Region"].isin(selected_regions if selected_regions else all_regions)) &
    (df_raw["Product_Category"].isin(selected_categories if selected_categories else all_categories)) &
    (df_raw["Customer_Segment"].isin(selected_segments if selected_segments else all_segments)) &
    (df_raw["Shipping_Status"].isin(selected_statuses if selected_statuses else all_statuses))
)

df_filtered = df_raw[mask]

# --- HEADER SECTION ---
st.title("📈 Executive Sales & Business Dashboard")
st.caption(f"Showing performance metrics from **{start_date}** to **{end_date}** | Total Transactions Filtered: **{len(df_filtered):,}**")

if df_filtered.empty:
    st.warning("⚠️ No data available matching the selected filter criteria. Please adjust your filters in the sidebar.")
    st.stop()

# --- KPI METRICS SECTION ---
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_revenue = df_filtered["Sales_Revenue"].sum()
total_profit = df_filtered["Profit"].sum()
avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
total_orders = len(df_filtered)
avg_order_val = total_revenue / total_orders if total_orders > 0 else 0
avg_satisfaction = df_filtered["Satisfaction_Rating"].mean()

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">${total_revenue/1e6:.2f}M</div>
            <div class="kpi-sub text-positive">↑ {total_revenue/1e3:,.0f}K Gross</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Profit</div>
            <div class="kpi-value">${total_profit/1e6:.2f}M</div>
            <div class="kpi-sub text-positive">Net Income</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Profit Margin</div>
            <div class="kpi-value">{avg_margin:.1f}%</div>
            <div class="kpi-sub text-neutral">Avg Return Rate</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Orders</div>
            <div class="kpi-value">{total_orders:,}</div>
            <div class="kpi-sub text-neutral">Transactions</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Order Value</div>
            <div class="kpi-value">${avg_order_val:,.0f}</div>
            <div class="kpi-sub text-neutral">Per Transaction</div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Satisfaction</div>
            <div class="kpi-value">⭐ {avg_satisfaction:.2f}</div>
            <div class="kpi-sub text-positive">Out of 5.0</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DASHBOARD TABS ---
tab_overview, tab_products, tab_regions, tab_raw_data = st.tabs([
    "📈 Executive Overview",
    "🛍️ Product & Category Analysis",
    "🌍 Regional & Customer Insights",
    "🔍 Data Explorer & Export"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab_overview:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Monthly Revenue & Profit Growth Trend")
        
        # Resample by Month
        df_monthly = df_filtered.set_index("Order_Date").resample("MS")[["Sales_Revenue", "Profit"]].sum().reset_index()
        df_monthly["Order_Date_Str"] = df_monthly["Order_Date"].dt.strftime("%b %Y")
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_monthly["Order_Date_Str"],
            y=df_monthly["Sales_Revenue"],
            name="Revenue ($)",
            mode="lines+markers",
            fill='tozeroy',
            line=dict(color="#3b82f6", width=3),
            fillcolor="rgba(59, 130, 246, 0.1)"
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_monthly["Order_Date_Str"],
            y=df_monthly["Profit"],
            name="Profit ($)",
            mode="lines+markers",
            line=dict(color="#10b981", width=3)
        ))
        fig_trend.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template="plotly_dark"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("Revenue Share by Category")
        df_cat_share = df_filtered.groupby("Product_Category")["Sales_Revenue"].sum().reset_index()
        
        fig_pie = px.pie(
            df_cat_share,
            values="Sales_Revenue",
            names="Product_Category",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False,
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Monthly Orders Count")
        df_orders_monthly = df_filtered.set_index("Order_Date").resample("MS")["Order_ID"].count().reset_index()
        df_orders_monthly["Order_Date_Str"] = df_orders_monthly["Order_Date"].dt.strftime("%b %Y")
        
        fig_orders = px.bar(
            df_orders_monthly,
            x="Order_Date_Str",
            y="Order_ID",
            labels={"Order_ID": "Number of Orders", "Order_Date_Str": "Month"},
            color_discrete_sequence=["#8b5cf6"]
        )
        fig_orders.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_orders, use_container_width=True)
        
    with col_b:
        st.subheader("Shipping Status Distribution")
        df_status = df_filtered["Shipping_Status"].value_counts().reset_index()
        df_status.columns = ["Status", "Count"]
        
        fig_status = px.bar(
            df_status,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map={"Delivered": "#10b981", "Shipped": "#3b82f6", "Processing": "#f59e0b", "Cancelled": "#ef4444"}
        )
        fig_status.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_status, use_container_width=True)

# ==========================================
# TAB 2: PRODUCT & CATEGORY PERFORMANCE
# ==========================================
with tab_products:
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        st.subheader("Top 10 Products by Sales Revenue")
        df_top_prod = df_filtered.groupby("Product_Name")[["Sales_Revenue", "Profit", "Quantity"]].sum().reset_index()
        df_top_prod = df_top_prod.sort_values(by="Sales_Revenue", ascending=True).tail(10)
        
        fig_top_prod = px.bar(
            df_top_prod,
            x="Sales_Revenue",
            y="Product_Name",
            orientation="h",
            text_auto=".2s",
            color="Profit",
            color_continuous_scale="Viridis",
            labels={"Sales_Revenue": "Sales Revenue ($)", "Product_Name": "Product"}
        )
        fig_top_prod.update_layout(height=420, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_top_prod, use_container_width=True)

    with p_col2:
        st.subheader("Category Profitability Comparison")
        df_cat_prof = df_filtered.groupby("Product_Category")[["Sales_Revenue", "Profit", "Cost"]].sum().reset_index()
        df_cat_prof["Margin_Pct"] = round(df_cat_prof["Profit"] / df_cat_prof["Sales_Revenue"] * 100, 1)
        
        fig_cat_prof = go.Figure()
        fig_cat_prof.add_trace(go.Bar(
            x=df_cat_prof["Product_Category"], y=df_cat_prof["Sales_Revenue"], name="Revenue", marker_color="#3b82f6"
        ))
        fig_cat_prof.add_trace(go.Bar(
            x=df_cat_prof["Product_Category"], y=df_cat_prof["Profit"], name="Profit", marker_color="#10b981"
        ))
        fig_cat_prof.update_layout(
            barmode="group",
            height=420,
            template="plotly_dark",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_cat_prof, use_container_width=True)

    st.subheader("Discount vs Profit Margin Scatter Plot")
    fig_scatter = px.scatter(
        df_filtered,
        x="Discount_Pct",
        y="Profit",
        size="Quantity",
        color="Product_Category",
        hover_data=["Order_ID", "Product_Name", "Customer_Segment"],
        labels={"Discount_Pct": "Discount Percentage", "Profit": "Order Profit ($)"},
        opacity=0.7
    )
    fig_scatter.update_layout(height=350, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# TAB 3: REGIONAL & CUSTOMER INSIGHTS
# ==========================================
with tab_regions:
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.subheader("Regional Revenue Performance")
        df_reg = df_filtered.groupby("Region")[["Sales_Revenue", "Profit"]].sum().reset_index().sort_values(by="Sales_Revenue", ascending=False)
        
        fig_reg = px.bar(
            df_reg,
            x="Region",
            y="Sales_Revenue",
            color="Region",
            text_auto=".2s",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            labels={"Sales_Revenue": "Revenue ($)"}
        )
        fig_reg.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_reg, use_container_width=True)

    with r_col2:
        st.subheader("Revenue by Customer Segment")
        df_seg = df_filtered.groupby("Customer_Segment")[["Sales_Revenue", "Order_ID"]].agg({"Sales_Revenue": "sum", "Order_ID": "count"}).reset_index()
        df_seg.rename(columns={"Order_ID": "Order_Count"}, inplace=True)
        
        fig_seg = px.treemap(
            df_seg,
            path=["Customer_Segment"],
            values="Sales_Revenue",
            color="Sales_Revenue",
            color_continuous_scale="Blues",
            labels={"Sales_Revenue": "Revenue ($)"}
        )
        fig_seg.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_seg, use_container_width=True)

    st.subheader("Country Breakdown within Selected Regions")
    df_country = df_filtered.groupby(["Region", "Country"])[["Sales_Revenue", "Profit"]].sum().reset_index()
    fig_country = px.bar(
        df_country,
        x="Country",
        y="Sales_Revenue",
        color="Region",
        text_auto=".2s",
        labels={"Sales_Revenue": "Revenue ($)"}
    )
    fig_country.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_country, use_container_width=True)

# ==========================================
# TAB 4: RAW DATA EXPLORER & EXPORT
# ==========================================
with tab_raw_data:
    st.subheader("Filtered Sales Transactions Table")
    
    # Search input
    search_query = st.text_input("🔍 Search orders (Customer ID, Product Name, Order ID, etc.):", "")
    
    df_display = df_filtered.copy()
    if search_query:
        query = search_query.lower()
        search_mask = (
            df_display["Order_ID"].astype(str).str.lower().str.contains(query) |
            df_display["Customer_ID"].astype(str).str.lower().str.contains(query) |
            df_display["Product_Name"].astype(str).str.lower().str.contains(query) |
            df_display["Country"].astype(str).str.lower().str.contains(query)
        )
        df_display = df_display[search_mask]
        
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Order_Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Unit_Price": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
            "Sales_Revenue": st.column_config.NumberColumn("Sales Revenue", format="$%.2f"),
            "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
            "Profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
            "Discount_Pct": st.column_config.NumberColumn("Discount", format="%.0f%%"),
            "Satisfaction_Rating": st.column_config.NumberColumn("Rating", format="⭐ %d"),
        }
    )
    
    col_ex1, col_ex2 = st.columns([1, 4])
    with col_ex1:
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    with col_ex2:
        st.caption(f"Exporting {len(df_display):,} records based on active filter selections.")
