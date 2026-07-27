import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from data_loader import (
    load_pmed_fod_data,
    load_rsbsa_data,
    load_test_excel_all_sheets,
    load_custom_excel,
    parse_google_sheet_url,
    load_sample_google_sheet_data,
    DEFAULT_GSHEET_URL
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DA-RFO CAR & Google Sheets Analytics Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LIGHT & DARK MODE COMPATIBLE STYLING ---
st.markdown("""
    <style>
    /* Global Container Padding */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Theme-Adaptive Executive KPI Metric Cards */
    .kpi-card {
        background-color: var(--secondary-background-color, rgba(255, 255, 255, 0.05));
        border-radius: 12px;
        padding: 18px 20px;
        color: var(--text-color, #111827);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-left: 5px solid #10b981;
        margin-bottom: 14px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.15);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.85;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .kpi-sub {
        font-size: 0.82rem;
        font-weight: 500;
    }
    .text-emerald { color: #10b981; font-weight: 600; }
    .text-amber { color: #f59e0b; font-weight: 600; }
    .text-blue { color: #3b82f6; font-weight: 600; }
    .text-purple { color: #8b5cf6; font-weight: 600; }
    
    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #047857 0%, #10b981 100%);
        padding: 20px 26px;
        border-radius: 14px;
        color: #ffffff !important;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
    }
    .header-banner h2, .header-banner p {
        color: #ffffff !important;
    }
    
    /* Light/Dark mode custom instructions container */
    .info-box {
        background-color: var(--secondary-background-color, rgba(16, 185, 129, 0.08));
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 18px;
        color: var(--text-color, #111827);
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to apply light/dark theme transparent backgrounds to Plotly figures
def apply_plotly_theme(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(size=12)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)")
    return fig

# --- LOAD DA-RFO CAR BASE DATASETS ---
@st.cache_data
def get_dashboard_data():
    df_pmed = load_pmed_fod_data()
    df_rsbsa = load_rsbsa_data()
    return df_pmed, df_rsbsa

df_pmed, df_rsbsa = get_dashboard_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/sprout.png", width=64)
st.sidebar.title("DA-RFO CAR Analytics")
st.sidebar.caption("Cordillera Administrative Region")

view_mode = st.sidebar.radio(
    "Select Dashboard View",
    [
        "🟢 Google Sheets & Custom Data",
        "📈 Commercial Sales & Ops (Excel)",
        "📊 Physical & Financial Accomplishments",
        "👨‍🌾 RSBSA Farmer & Fisher Registry"
    ]
)

st.sidebar.markdown("---")

# =======================================================
# VIEW 1: GOOGLE SHEETS LIVE INTEGRATION & UPLOAD
# =======================================================
if view_mode == "🟢 Google Sheets & Custom Data":
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0;">📊 Google Sheets & External Data Analytics</h2>
            <p style="margin:4px 0 0 0; font-size:1.05rem; opacity:0.95;">
                Connect live Google Sheets via URL or test with pre-built Google Sheets datasets.
            </p>
        </div>
    """, unsafe_allow_html=True)

    data_source_type = st.sidebar.selectbox(
        "Choose Data Connection",
        [
            "🔗 Connect Google Sheet via Link/URL",
            "⚡ Local Google Sheets Dataset (CSV)",
            "📁 Upload File (.xlsx / .csv)"
        ]
    )

    df_gsheet = pd.DataFrame()
    source_name = ""

    if data_source_type == "🔗 Connect Google Sheet via Link/URL":
        st.subheader("🔗 Connect Live Google Sheets Document")
        
        st.markdown("""
            <div class="info-box">
                <b>💡 Connected Google Sheet:</b><br/>
                You can view the live Google Sheet directly or replace the link below with any other Google Sheets document.<br/>
                <i>(Ensure the sheet sharing is set to "Anyone with the link can view")</i>
            </div>
        """, unsafe_allow_html=True)
        
        gsheet_url = st.text_input(
            "Google Sheets Link / URL",
            value=DEFAULT_GSHEET_URL
        )
        
        if gsheet_url:
            try:
                with st.spinner("Fetching live data from Google Sheets..."):
                    df_gsheet = parse_google_sheet_url(gsheet_url)
                    source_name = "Live Google Sheet"
                    st.success(f"✅ Connected! Loaded {len(df_gsheet):,} records live from Google Sheets.")
            except Exception as e:
                st.error(f"❌ Failed to load Google Sheet: {e}")
                st.info("Falling back to local cached copy...")
                df_gsheet = load_sample_google_sheet_data()
                source_name = "Local Google Sheets Dataset (Fallback)"
        else:
            st.info("Enter a Google Sheets link above.")

    elif data_source_type == "⚡ Local Google Sheets Dataset (CSV)":
        df_gsheet = load_sample_google_sheet_data()
        source_name = "Local Google Sheets Dataset (google_sheets_dataset.csv)"
        st.success(f"✅ Loaded local Google Sheets dataset ({len(df_gsheet):,} records).")

    elif data_source_type == "📁 Upload File (.xlsx / .csv)":
        st.subheader("📁 Upload Exported Google Sheet or Local Dataset")
        uploaded_file = st.file_uploader("Upload .xlsx or .csv file", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            filename = uploaded_file.name
            try:
                if filename.endswith(".csv"):
                    df_gsheet = pd.read_csv(uploaded_file)
                    source_name = f"Uploaded CSV: {filename}"
                else:
                    sheets, dfs = load_custom_excel(uploaded_file)
                    if len(sheets) > 1:
                        selected_s = st.selectbox("Select Excel Sheet", sheets)
                        df_gsheet = dfs[selected_s]
                    else:
                        df_gsheet = dfs[sheets[0]]
                    source_name = f"Uploaded Excel: {filename}"
                st.success(f"✅ Loaded dataset from {source_name}")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

    # Display Dashboard if DataFrame loaded
    if not df_gsheet.empty:
        st.markdown("---")
        st.subheader(f"📊 Dashboard Analytics - {source_name}")

        # Auto-detect numerical and categorical columns
        num_cols = df_gsheet.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df_gsheet.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # --- KPI CARDS ---
        col1, col2, col3, col4 = st.columns(4)
        
        total_rows = len(df_gsheet)
        total_cols = len(df_gsheet.columns)
        
        rev_col = next((c for c in num_cols if "revenue" in c.lower() or "actual" in c.lower() or "sales" in c.lower() or "amount" in c.lower()), None)
        profit_col = next((c for c in num_cols if "profit" in c.lower() or "disbursement" in c.lower()), None)
        rating_col = next((c for c in num_cols if "score" in c.lower() or "rating" in c.lower() or "satisfaction" in c.lower()), None)

        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total Records</div>
                    <div class="kpi-value">{total_rows:,}</div>
                    <div class="kpi-sub text-emerald">Rows Processed</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            val_str = f"₱{df_gsheet[rev_col].sum():,.2f}" if rev_col else f"{total_cols} Columns"
            label_str = rev_col.replace("_", " ") if rev_col else "Total Attributes"
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{label_str}</div>
                    <div class="kpi-value">{val_str}</div>
                    <div class="kpi-sub text-amber">Sum Total</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            val_str = f"₱{df_gsheet[profit_col].sum():,.2f}" if profit_col else (f"₱{df_gsheet[num_cols[0]].mean():,.2f}" if num_cols else "N/A")
            label_str = profit_col.replace("_", " ") if profit_col else (f"Avg {num_cols[0]}" if num_cols else "Metric")
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{label_str}</div>
                    <div class="kpi-value">{val_str}</div>
                    <div class="kpi-sub text-blue">Calculated Metric</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            val_str = f"{df_gsheet[rating_col].mean():.2f} / 5.0" if rating_col else f"{len(cat_cols)} Categories"
            label_str = "Avg Rating" if rating_col else "Categorical Dimensions"
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{label_str}</div>
                    <div class="kpi-value">{val_str}</div>
                    <div class="kpi-sub text-purple">Overview Score</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- DYNAMIC CHARTS ---
        c1, c2 = st.columns([3, 2])
        
        with c1:
            st.subheader("Categorical Breakdown")
            group_cat = st.selectbox("Select Grouping Column", cat_cols if cat_cols else df_gsheet.columns, index=0)
            metric_num = st.selectbox("Select Metric Column", num_cols if num_cols else df_gsheet.columns, index=0)
            
            df_grouped = df_gsheet.groupby(group_cat)[metric_num].sum().reset_index().sort_values(by=metric_num, ascending=False).head(12)
            
            fig_bar = px.bar(
                df_grouped,
                x=metric_num,
                y=group_cat,
                orientation="h",
                text_auto=",.0f" if "PHP" in metric_num or df_grouped[metric_num].max() > 1000 else ".2f",
                color=metric_num,
                color_continuous_scale="Viridis",
                labels={metric_num: metric_num.replace("_", " "), group_cat: group_cat.replace("_", " ")}
            )
            apply_plotly_theme(fig_bar, height=380)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("Distribution Breakdown")
            pie_col = st.selectbox("Select Slice Dimension", cat_cols if len(cat_cols)>1 else cat_cols, index=min(1, len(cat_cols)-1) if cat_cols else 0)
            
            fig_pie = px.pie(
                df_gsheet,
                names=pie_col,
                values=metric_num if num_cols else None,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Emerald
            )
            apply_plotly_theme(fig_pie, height=380)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Detailed Table
        st.markdown("---")
        st.subheader("📋 Dataset Preview & Search")
        st.dataframe(df_gsheet, use_container_width=True, hide_index=True)
        
        csv_data = df_gsheet.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Processed Dataset (CSV)",
            data=csv_data,
            file_name=f"Google_Sheets_Export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# =======================================================
# VIEW 2: COMMERCIAL SALES & OPERATIONS (EXCEL DATASET)
# =======================================================
elif view_mode == "📈 Commercial Sales & Ops (Excel)":
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0;">📈 Commercial Sales & Agricultural Logistics</h2>
            <p style="margin:4px 0 0 0; font-size:1.05rem; opacity:0.95;">
                Multi-Tab Excel Dataset Analytics (sample_excel_test_data.xlsx)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    excel_data = load_test_excel_all_sheets()
    
    if not excel_data:
        st.warning("Excel test dataset not found. Generating now...")
        from generate_excel_data import generate_excel_test_dataset
        generate_excel_test_dataset()
        excel_data = load_test_excel_all_sheets()

    tab_names = list(excel_data.keys())
    selected_tab = st.sidebar.radio("Select Excel Sheet / Module", tab_names)
    
    df_active = excel_data[selected_tab]
    
    st.subheader(f"📑 Sheet: {selected_tab}")
    
    if selected_tab == "Sales_&_Operations":
        # Filters
        provinces = ["All"] + sorted(df_active["Province"].unique().tolist())
        sel_prov = st.sidebar.selectbox("Province Filter", provinces)
        
        categories = ["All"] + sorted(df_active["Category"].unique().tolist())
        sel_cat = st.sidebar.selectbox("Category Filter", categories)
        
        df_filtered = df_active.copy()
        if sel_prov != "All":
            df_filtered = df_filtered[df_filtered["Province"] == sel_prov]
        if sel_cat != "All":
            df_filtered = df_filtered[df_filtered["Category"] == sel_cat]
            
        # KPI Cards
        tot_target = df_filtered["Target_Revenue_PHP"].sum()
        tot_actual = df_filtered["Actual_Revenue_PHP"].sum()
        tot_profit = df_filtered["Net_Profit_PHP"].sum()
        avg_rating = df_filtered["Satisfaction_Score"].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Target Revenue</div>
                    <div class="kpi-value">₱{tot_target/1e6:.2f}M</div>
                    <div class="kpi-sub text-emerald">₱{tot_target:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Actual Revenue</div>
                    <div class="kpi-value">₱{tot_actual/1e6:.2f}M</div>
                    <div class="kpi-sub text-emerald">Achieved: {(tot_actual/tot_target*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Net Profit Margin</div>
                    <div class="kpi-value">₱{tot_profit/1e6:.2f}M</div>
                    <div class="kpi-sub text-amber">Margin: {(tot_profit/tot_actual*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Satisfaction Score</div>
                    <div class="kpi-value">{avg_rating:.2f} / 5.0</div>
                    <div class="kpi-sub text-blue">Customer Feedback</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        c1, c2 = st.columns([3, 2])
        with c1:
            st.subheader("Revenue by Equipment & Product Category")
            df_cat_rev = df_filtered.groupby("Category")[["Target_Revenue_PHP", "Actual_Revenue_PHP"]].sum().reset_index()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_cat_rev["Category"], y=df_cat_rev["Target_Revenue_PHP"], name="Target Revenue", marker_color="#059669"))
            fig_bar.add_trace(go.Bar(x=df_cat_rev["Category"], y=df_cat_rev["Actual_Revenue_PHP"], name="Actual Revenue", marker_color="#34d399"))
            apply_plotly_theme(fig_bar, height=380)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            st.subheader("Province Revenue Share")
            fig_pie = px.pie(df_filtered, names="Province", values="Actual_Revenue_PHP", hole=0.45, color_discrete_sequence=px.colors.qualitative.Dark2)
            apply_plotly_theme(fig_pie, height=380)
            st.plotly_chart(fig_pie, use_container_width=True)

    elif selected_tab == "Project_Tracker":
        tot_phys_t = df_active["Physical_Target_Units"].sum()
        tot_phys_a = df_active["Physical_Actual_Units"].sum()
        tot_ob_t = df_active["Obligation_Target_kPHP"].sum()
        tot_ob_a = df_active["Obligation_Actual_kPHP"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Physical Targets</div>
                    <div class="kpi-value">{tot_phys_t:,}</div>
                    <div class="kpi-sub text-emerald">Units</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Physical Accomplished</div>
                    <div class="kpi-value">{tot_phys_a:,}</div>
                    <div class="kpi-sub text-emerald">Rate: {(tot_phys_a/tot_phys_t*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Budget Target</div>
                    <div class="kpi-value">₱{tot_ob_t/1e3:.2f}M</div>
                    <div class="kpi-sub text-amber">₱{tot_ob_t:,.0f} K</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Budget Obligated</div>
                    <div class="kpi-value">₱{tot_ob_a/1e3:.2f}M</div>
                    <div class="kpi-sub text-blue">Rate: {(tot_ob_a/tot_ob_t*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        fig_proj = px.bar(
            df_active,
            x="Accomplishment_Rate_Pct",
            y="Program_Name",
            color="Status",
            orientation="h",
            labels={"Accomplishment_Rate_Pct": "Accomplishment Rate (%)", "Program_Name": "Program / Activity"}
        )
        apply_plotly_theme(fig_proj, height=400)
        st.plotly_chart(fig_proj, use_container_width=True)

    else:
        st.dataframe(df_active, use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.subheader("Data Table View")
    st.dataframe(df_active, use_container_width=True, hide_index=True)

# =======================================================
# VIEW 3: PHYSICAL & FINANCIAL ACCOMPLISHMENTS (DA CAR)
# =======================================================
elif view_mode == "📊 Physical & Financial Accomplishments":
    st.sidebar.subheader("PPA Filters")
    divisions = ["All"] + sorted(df_pmed["Division"].unique().tolist()) if not df_pmed.empty else ["All"]
    selected_div = st.sidebar.selectbox("Division", divisions)
    
    df_filtered_pmed = df_pmed.copy()
    if selected_div != "All" and not df_pmed.empty:
        df_filtered_pmed = df_filtered_pmed[df_filtered_pmed["Division"] == selected_div]
        
    # --- HEADER ---
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0;">🌾 Department of Agriculture - RFO CAR</h2>
            <p style="margin:4px 0 0 0; font-size:1.05rem; opacity:0.95;">Physical and Financial Accomplishment Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not df_filtered_pmed.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        tot_p_target = df_filtered_pmed["Physical_Annual_Target"].sum()
        tot_p_actual = df_filtered_pmed["Physical_Annual_Actual"].sum()
        p_rate = (tot_p_actual / tot_p_target * 100) if tot_p_target > 0 else 0.0
        
        tot_ob_target = df_filtered_pmed["Obligation_Target_kPHP"].sum()
        tot_ob_actual = df_filtered_pmed["Obligation_Actual_kPHP"].sum()
        ob_rate = (tot_ob_actual / tot_ob_target * 100) if tot_ob_target > 0 else 0.0
        
        tot_disb_target = df_filtered_pmed["Disbursement_Target_kPHP"].sum()
        tot_disb_actual = df_filtered_pmed["Disbursement_Actual_kPHP"].sum()
        disb_rate = (tot_disb_actual / tot_disb_target * 100) if tot_disb_target > 0 else 0.0
        
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Physical Target</div>
                    <div class="kpi-value">{tot_p_target:,.0f}</div>
                    <div class="kpi-sub text-emerald">Units / Deliverables</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Physical Actual</div>
                    <div class="kpi-value">{tot_p_actual:,.0f}</div>
                    <div class="kpi-sub text-emerald">Rate: {p_rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Obligation Target</div>
                    <div class="kpi-value">₱{tot_ob_target/1e3:.2f}M</div>
                    <div class="kpi-sub text-amber">₱{tot_ob_target:,.0f} K</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Obligation Actual</div>
                    <div class="kpi-value">₱{tot_ob_actual/1e3:.2f}M</div>
                    <div class="kpi-sub text-amber">Rate: {ob_rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col5:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Disbursement Actual</div>
                    <div class="kpi-value">₱{tot_disb_actual/1e3:.2f}M</div>
                    <div class="kpi-sub text-blue">Rate: {disb_rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CHARTS ---
        tab1, tab2 = st.tabs(["📊 Physical Performance", "💰 Financial Performance"])
        
        with tab1:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.subheader("Physical Accomplishment Rate (%) by Program / Activity")
                fig_p = px.bar(
                    df_filtered_pmed,
                    x="Physical_Rate_Pct",
                    y="PPA_Name",
                    orientation="h",
                    text="Physical_Rate_Pct",
                    color="Physical_Rate_Pct",
                    color_continuous_scale="Greens",
                    labels={"Physical_Rate_Pct": "Accomplishment Rate (%)", "PPA_Name": "PPA / Activity"}
                )
                fig_p.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                apply_plotly_theme(fig_p, height=380)
                st.plotly_chart(fig_p, use_container_width=True)
                
            with c2:
                st.subheader("Quarterly Target vs Actual Breakdown")
                q_data = pd.DataFrame({
                    "Quarter": ["Q1", "Q2", "Q3", "Q4"],
                    "Target": [
                        df_filtered_pmed["Physical_Target_Q1"].sum(),
                        df_filtered_pmed["Physical_Target_Q2"].sum(),
                        df_filtered_pmed["Physical_Target_Q3"].sum(),
                        df_filtered_pmed["Physical_Target_Q4"].sum()
                    ],
                    "Actual": [
                        df_filtered_pmed["Physical_Actual_Q1"].sum(),
                        df_filtered_pmed["Physical_Actual_Q2"].sum(),
                        df_filtered_pmed["Physical_Actual_Q3"].sum(),
                        df_filtered_pmed["Physical_Actual_Q4"].sum()
                    ]
                })
                
                fig_q = go.Figure()
                fig_q.add_trace(go.Bar(x=q_data["Quarter"], y=q_data["Target"], name="Target", marker_color="#059669"))
                fig_q.add_trace(go.Bar(x=q_data["Quarter"], y=q_data["Actual"], name="Actual", marker_color="#34d399"))
                fig_q.update_layout(barmode="group")
                apply_plotly_theme(fig_q, height=380)
                st.plotly_chart(fig_q, use_container_width=True)
                
        with tab2:
            st.subheader("Financial Performance (in Thousands PHP)")
            fig_fin = go.Figure()
            fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Obligation_Target_kPHP"], name="Obligation Target (₱ '000)", marker_color="#f59e0b"))
            fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Obligation_Actual_kPHP"], name="Obligation Actual (₱ '000)", marker_color="#fbbf24"))
            fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Disbursement_Actual_kPHP"], name="Disbursement Actual (₱ '000)", marker_color="#3b82f6"))
            fig_fin.update_layout(barmode="group")
            apply_plotly_theme(fig_fin, height=400)
            st.plotly_chart(fig_fin, use_container_width=True)
            
        st.markdown("---")
        st.subheader("Detailed Accomplishment Table")
        st.dataframe(df_filtered_pmed, use_container_width=True, hide_index=True)
    else:
        st.info("No records found for the selected division.")

# =======================================================
# VIEW 4: RSBSA FARMER & FISHER REGISTRY ANALYTICS
# =======================================================
else:
    st.sidebar.subheader("RSBSA Filters")
    status_options = ["All"] + sorted(df_rsbsa["Status"].unique().tolist()) if not df_rsbsa.empty else ["All"]
    selected_status = st.sidebar.selectbox("Record Status", status_options)
    
    regions = ["All", "CAR Only"] + sorted(df_rsbsa["Region"].unique().tolist()) if not df_rsbsa.empty else ["All"]
    selected_region = st.sidebar.selectbox("Region Filter", regions)
    
    df_filtered_rsbsa = df_rsbsa.copy()
    if not df_filtered_rsbsa.empty:
        if selected_status != "All":
            df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Status"] == selected_status]
            
        if selected_region == "CAR Only":
            df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Region"].str.contains("CORDILLERA", case=False, na=False)]
        elif selected_region != "All":
            df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Region"] == selected_region]

    # --- HEADER ---
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0;">🌾 RSBSA Farmer & Fisher Registry Analytics</h2>
            <p style="margin:4px 0 0 0; font-size:1.05rem; opacity:0.95;">Registry System for Basic Sectors in Agriculture | DA-RFO CAR</p>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered_rsbsa.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        tot_2024 = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Total_2024"].sum()
        tot_2025 = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Total_2025"].sum()
        grand_tot = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Grand_Total"].sum()
        
        df_car = df_rsbsa[df_rsbsa["Region"].str.contains("CORDILLERA", case=False, na=False) & df_rsbsa["Is_Province"]]
        car_tot = df_car["Grand_Total"].sum()
        
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Grand Total Records</div>
                    <div class="kpi-value">{grand_tot:,}</div>
                    <div class="kpi-sub text-emerald">Verified & Registered</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">CAR Region Records</div>
                    <div class="kpi-value">{car_tot:,}</div>
                    <div class="kpi-sub text-emerald">Cordillera Administrative</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">2024 Total Records</div>
                    <div class="kpi-value">{tot_2024:,}</div>
                    <div class="kpi-sub text-amber">Prior Year Baseline</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">2025 Total Records</div>
                    <div class="kpi-value">{tot_2025:,}</div>
                    <div class="kpi-sub text-blue">Current Year Progress</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)

        # --- CHARTS ---
        c1, c2 = st.columns([3, 2])
        
        with c1:
            st.subheader("CAR Province Registration Breakdown")
            df_car_prov = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"] & df_filtered_rsbsa["Region"].str.contains("CORDILLERA", case=False, na=False)]
            df_car_sum = df_car_prov.groupby("Name")[["Total_2024", "Total_2025", "Grand_Total"]].sum().reset_index()
            
            fig_car = px.bar(
                df_car_sum,
                x="Grand_Total",
                y="Name",
                orientation="h",
                text_auto=",",
                color="Grand_Total",
                color_continuous_scale="Greens",
                labels={"Grand_Total": "Registered Farmers / Fishers", "Name": "Province"}
            )
            apply_plotly_theme(fig_car, height=380)
            st.plotly_chart(fig_car, use_container_width=True)

        with c2:
            st.subheader("Records by Status Type")
            df_status_sum = df_rsbsa[df_rsbsa["Is_Province"]].groupby("Status")["Grand_Total"].sum().reset_index()
            
            fig_status = px.pie(
                df_status_sum,
                values="Grand_Total",
                names="Status",
                hole=0.45,
                color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b"]
            )
            apply_plotly_theme(fig_status, height=380)
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")
        st.subheader("Monthly Registration Velocity (2025)")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_vals = [df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]][m].sum() for m in months]
        df_monthly = pd.DataFrame({"Month": months, "Registrations": monthly_vals})
        
        fig_m = px.area(
            df_monthly,
            x="Month",
            y="Registrations",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#10b981"]
        )
        apply_plotly_theme(fig_m, height=320)
        st.plotly_chart(fig_m, use_container_width=True)

        st.markdown("---")
        st.subheader("Detailed RSBSA Registry Data")
        st.dataframe(df_filtered_rsbsa, use_container_width=True, hide_index=True)
    else:
        st.info("No records found for selected filters.")
