import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from data_loader import load_pmed_fod_data, load_rsbsa_data

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DA-RFO CAR Accomplishment & RSBSA Dashboard",
    page_icon="🌾",
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
    
    /* DA CAR Executive KPI Metric Cards */
    .kpi-card {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border-radius: 12px;
        padding: 18px 20px;
        color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin-bottom: 12px;
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #a7f3d0;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
    }
    .text-emerald { color: #34d399; }
    .text-amber { color: #fbbf24; }
    .text-blue { color: #60a5fa; }
    
    /* Header banner */
    .header-banner {
        background: linear-gradient(90deg, #047857 0%, #10b981 100%);
        padding: 16px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def get_dashboard_data():
    df_pmed = load_pmed_fod_data()
    df_rsbsa = load_rsbsa_data()
    return df_pmed, df_rsbsa

df_pmed, df_rsbsa = get_dashboard_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.image("https://img.icons8.com/color/96/sprout.png", width=64)
st.sidebar.title("DA-RFO CAR Analytics")
st.sidebar.caption("Cordillera Administrative Region")

view_mode = st.sidebar.radio(
    "Select Dashboard View",
    ["📊 Physical & Financial Accomplishments", "👨‍🌾 RSBSA Farmer & Fisher Registry"]
)

st.sidebar.markdown("---")

if view_mode == "📊 Physical & Financial Accomplishments":
    st.sidebar.subheader("PPA Filters")
    divisions = ["All"] + sorted(df_pmed["Division"].unique().tolist())
    selected_div = st.sidebar.selectbox("Division", divisions)
    
    df_filtered_pmed = df_pmed.copy()
    if selected_div != "All":
        df_filtered_pmed = df_filtered_pmed[df_filtered_pmed["Division"] == selected_div]
        
    # --- HEADER ---
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0; color:white;">🌾 Department of Agriculture - RFO CAR</h2>
            <p style="margin:4px 0 0 0; font-size:1rem; opacity:0.9;">Physical and Financial Accomplishment Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- KPI METRICS ---
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
                <div class="kpi-title">Physical Accomplished</div>
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
    tab1, tab2 = st.tabs(["📊 Physical Performance", "💰 Financial Obligations & Disbursements"])
    
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
            fig_p.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
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
            fig_q.update_layout(barmode="group", height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_q, use_container_width=True)
            
    with tab2:
        st.subheader("Financial Performance (in Thousands PHP)")
        fig_fin = go.Figure()
        fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Obligation_Target_kPHP"], name="Obligation Target (₱ '000)", marker_color="#f59e0b"))
        fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Obligation_Actual_kPHP"], name="Obligation Actual (₱ '000)", marker_color="#fbbf24"))
        fig_fin.add_trace(go.Bar(x=df_filtered_pmed["PPA_Name"], y=df_filtered_pmed["Disbursement_Actual_kPHP"], name="Disbursement Actual (₱ '000)", marker_color="#3b82f6"))
        fig_fin.update_layout(barmode="group", height=400, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_fin, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Detailed Accomplishment Table")
    st.dataframe(df_filtered_pmed, use_container_width=True, hide_index=True)
    
    csv_pmed = df_filtered_pmed.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export PPA Report CSV",
        data=csv_pmed,
        file_name=f"DA_CAR_PPA_Accomplishment_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# =======================================================
# VIEW 2: RSBSA FARMER & FISHER REGISTRATION ANALYTICS
# =======================================================
else:
    st.sidebar.subheader("RSBSA Filters")
    status_options = ["All"] + sorted(df_rsbsa["Status"].unique().tolist())
    selected_status = st.sidebar.selectbox("Record Status", status_options)
    
    regions = ["All", "CAR Only"] + sorted(df_rsbsa["Region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Region Filter", regions)
    
    df_filtered_rsbsa = df_rsbsa.copy()
    if selected_status != "All":
        df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Status"] == selected_status]
        
    if selected_region == "CAR Only":
        df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Region"].str.contains("CORDILLERA", case=False, na=False)]
    elif selected_region != "All":
        df_filtered_rsbsa = df_filtered_rsbsa[df_filtered_rsbsa["Region"] == selected_region]

    # --- HEADER ---
    st.markdown("""
        <div class="header-banner">
            <h2 style="margin:0; padding:0; color:white;">🌾 RSBSA Farmer & Fisher Registry Analytics</h2>
            <p style="margin:4px 0 0 0; font-size:1rem; opacity:0.9;">Registry System for Basic Sectors in Agriculture | DA-RFO CAR</p>
        </div>
    """, unsafe_allow_html=True)

    # --- KPI METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    
    tot_2024 = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Total_2024"].sum()
    tot_2025 = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Total_2025"].sum()
    grand_tot = df_filtered_rsbsa[df_filtered_rsbsa["Is_Province"]]["Grand_Total"].sum()
    
    # CAR specific count
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
        fig_car.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
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
        fig_status.update_layout(height=380, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
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
    fig_m.update_layout(height=320, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")
    st.subheader("Detailed RSBSA Registry Data")
    st.dataframe(df_filtered_rsbsa, use_container_width=True, hide_index=True)
    
    csv_rsbsa = df_filtered_rsbsa.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export RSBSA Data CSV",
        data=csv_rsbsa,
        file_name=f"DA_CAR_RSBSA_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
