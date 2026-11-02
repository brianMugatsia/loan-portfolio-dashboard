import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------- Page Configuration -----------------------------
st.set_page_config(
    page_title="Executive Loan Portfolio Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Vivid & Stylish Theme (CSS) -----------------------------
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
      
      @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
      }

      /* Stylish Colorful Gradient Metric Cards */
      .metric-card {
          background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
          border: 1px solid #cbd5e1;
          border-radius: 16px;
          padding: 22px;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
          position: relative;
          overflow: hidden;
          animation: fadeInUp 0.5s ease-out forwards;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      .metric-card:nth-child(1) { border-left: 6px solid #3b82f6; }
      .metric-card:nth-child(2) { border-left: 6px solid #10b981; }
      .metric-card:nth-child(3) { border-left: 6px solid #8b5cf6; }
      .metric-card:nth-child(4) { border-left: 6px solid #f59e0b; }

      .metric-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
          border-color: #94a3b8;
      }

      .metric-title {
          font-size: 0.78rem;
          font-weight: 800;
          color: #475569;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-bottom: 8px;
      }
      
      .metric-value {
          font-size: 1.45rem;
          font-weight: 800;
          color: #0f172a;
          letter-spacing: -0.025em;
      }

      /* Executive Health Badge */
      .health-banner {
          padding: 14px 20px;
          border-radius: 12px;
          background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
          color: #ffffff;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
          margin-bottom: 24px;
      }

      h1, h2, h3 { color: #1e3a8a; }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETTE = {
    "primary": "#3b82f6",
    "teal": "#06b6d4",
    "indigo": "#6366f1",
    "green": "#10b981",
    "amber": "#f59e0b",
    "rose": "#f43f5e",
    "purple": "#8b5cf6",
}

REQUIRED_COLUMNS = [
    "Branch",
    "Loan Type",
    "Disbursement Date",
    "Principal Amount",
    "Outstanding Balance",
    "Status",
]

OPTIONAL_COLUMNS = ["Interest Rate (%)", "Credit Score", "Risk Rating"]


# ----------------------------- Helper Components -----------------------------
def render_metric_card(title: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------- Data Processing -----------------------------
@st.cache_data(show_spinner="Analyzing portfolio records...")
def read_uploaded_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(io.BytesIO(file_bytes))
    if suffix == ".csv":
        return pd.read_csv(io.BytesIO(file_bytes))
    raise ValueError("Unsupported format. Please upload an .xlsx, .xls, or .csv file.")


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = df.columns.astype(str).str.strip()

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}. "
            "Please check that your file headers match the expected schema."
        )

    numeric_cols = ["Principal Amount", "Outstanding Balance", "Interest Rate (%)", "Credit Score"]
    for col in numeric_cols:
        if col in df.columns:
            cleaned = (
                df[col]
                .astype(str)
                .str.replace(r"[^\d.-]", "", regex=True)
                .str.strip()
            )
            df[col] = pd.to_numeric(cleaned, errors="coerce")

    df["Disbursement Date"] = pd.to_datetime(df["Disbursement Date"], errors="coerce")
    
    for col in ["Branch", "Loan Type", "Status"]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    if "Risk Rating" in df.columns:
        df["Risk Rating"] = df["Risk Rating"].fillna("Unrated").astype(str).str.strip()

    df = df.dropna(subset=["Disbursement Date", "Principal Amount", "Outstanding Balance"])
    df = df[df["Principal Amount"] >= 0]
    df["Outstanding Balance"] = df["Outstanding Balance"].clip(lower=0)

    if df.empty:
        raise ValueError("No valid loan records remained after data cleaning.")

    return df


def money(value: float) -> str:
    return f"KSh {value:,.2f}"


# ----------------------------- Sidebar Hub -----------------------------
with st.sidebar:
    st.title("📂 Data Control Center")
    uploaded = st.file_uploader(
        "Upload Portfolio File",
        type=["xlsx", "xls", "csv"],
        help="Upload an Excel workbook or CSV portfolio file.",
    )
    
    st.divider()
    st.markdown("**📋 Schema Checklist**")
    st.caption("Required: " + ", ".join(REQUIRED_COLUMNS))
    st.caption("Optional: " + ", ".join(OPTIONAL_COLUMNS))


# ----------------------------- Landing State -----------------------------
if uploaded is None:
    st.title("💎 Executive Loan Portfolio Intelligence")
    st.caption("Next-generation interactive lending analytics, branch performance, and risk management.")
    
    st.info("👈 Upload your loan data workbook in the sidebar to launch the dashboard.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("### 📊 Advanced KPIs")
        st.write("Track real-time Portfolio at Risk (PAR), total exposures, and recovery metrics.")
    with col_b:
        st.markdown("### 🗺️ Branch Insights")
        st.write("Compare branch concentration, credit quality, and loan book health instantly.")
    with col_c:
        st.markdown("### ⚡ Fully Interactive")
        st.write("Dynamic timeline trends, segmentation filters, and instant CSV export features.")
    st.stop()


# ----------------------------- Load & Clean Data -----------------------------
try:
    raw_df = read_uploaded_file(uploaded.getvalue(), uploaded.name)
    df = clean_data(raw_df)
except Exception as exc:
    st.error(f"⚠️ Failed to process file: {exc}")
    st.stop()


# ----------------------------- Interactive Filtering Hub -----------------------------
with st.sidebar:
    st.divider()
    st.header("🔍 Dynamic Filters")
    
    branch_options = sorted(df["Branch"].unique())
    type_options = sorted(df["Loan Type"].unique())
    status_options = sorted(df["Status"].unique())

    selected_branches = st.multiselect("Filter Branch", branch_options, default=branch_options)
    selected_types = st.multiselect("Filter Loan Type", type_options, default=type_options)
    selected_statuses = st.multiselect("Filter Status", status_options, default=status_options)

    min_date = df["Disbursement Date"].min().date()
    max_date = df["Disbursement Date"].max().date()
    
    date_range = st.date_input(
        "Disbursement Timeline",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

filtered = df[
    df["Branch"].isin(selected_branches)
    & df["Loan Type"].isin(selected_types)
    & df["Status"].isin(selected_statuses)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Disbursement Date"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("⚠️ No loan records match your current filter selection. Please adjust your criteria.")
    st.stop()


# ----------------------------- Calculated Analytics -----------------------------
total_loans = len(filtered)
total_principal = filtered["Principal Amount"].sum()
total_outstanding = filtered["Outstanding Balance"].sum()

avg_interest = filtered["Interest Rate (%)"].dropna().mean() if "Interest Rate (%)" in filtered.columns else None
avg_credit_score = filtered["Credit Score"].dropna().mean() if "Credit Score" in filtered.columns else None

risk_statuses = filtered["Status"].str.casefold().isin(["overdue", "defaulted", "in arrears", "arrears"])
risk_balance = filtered.loc[risk_statuses, "Outstanding Balance"].sum()
par = (risk_balance / total_outstanding * 100) if total_outstanding > 0 else 0.0

# Portfolio Health Grade
if par < 3.0:
    health_grade, health_color = "🟢 Grade A (Healthy Portfolio)", "#10b981"
elif par < 7.0:
    health_grade, health_color = "🟡 Grade B (Moderate Risk)", "#f59e0b"
else:
    health_grade, health_color = "🔴 Grade C (High Risk / Action Required)", "#f43f5e"


# ----------------------------- Main Layout Dashboard -----------------------------
st.title("💎 Loan Portfolio Intelligence Hub")
st.caption("Comprehensive risk visibility, credit distribution, and disbursement performance.")

# Executive Health Banner
st.markdown(
    f"""
    <div class="health-banner">
        <div>
            <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8;">Portfolio Health Status</span>
            <div style="font-size: 1.1rem; font-weight: 700; color: {health_color}; margin-top: 2px;">{health_grade}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8;">Active Filter Scope</span>
            <div style="font-size: 1rem; font-weight: 600; color: #e2e8f0;">{total_loans:,} Active Loans / {filtered['Branch'].nunique()} Branches</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- KPI Cards Grid -----------------------------
st.subheader("📊 Core Portfolio Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Total Active Loans", f"{total_loans:,}")
with col2:
    render_metric_card("Total Principal Disbursed", money(total_principal))
with col3:
    render_metric_card("Total Outstanding Balance", money(total_outstanding))
with col4:
    render_metric_card("Portfolio at Risk (PAR)", f"{par:.2f}%")

st.write("") 

col5, col6, col7, col8 = st.columns(4)
with col5:
    avg_int_str = f"{avg_interest:.2f}%" if avg_interest is not None and pd.notna(avg_interest) else "N/A"
    render_metric_card("Average Interest Rate", avg_int_str)
with col6:
    avg_cs_str = f"{avg_credit_score:,.0f}" if avg_credit_score is not None and pd.notna(avg_credit_score) else "N/A"
    render_metric_card("Average Credit Score", avg_cs_str)
with col7:
    render_metric_card("At-Risk Balance", money(risk_balance))
with col8:
    render_metric_card("Active Branches", f"{filtered['Branch'].nunique():,}")

st.divider()

# ----------------------------- Colorful Advanced Charts -----------------------------
st.subheader("📈 Multi-Dimensional Portfolio Analytics")

chart_row1_left, chart_row1_right = st.columns(2)

with chart_row1_left:
    st.markdown("#### Principal vs. Outstanding by Loan Type")
    by_type = (
        filtered.groupby("Loan Type", as_index=False)
        .agg(
            Principal=("Principal Amount", "sum"),
            Outstanding=("Outstanding Balance", "sum"),
        )
        .sort_values("Principal", ascending=False)
    )
    fig_type = go.Figure()
    fig_type.add_bar(
        name="Principal Disbursed",
        x=by_type["Loan Type"],
        y=by_type["Principal"],
        marker_color=PALETTE["primary"],
    )
    fig_type.add_bar(
        name="Outstanding Balance",
        x=by_type["Loan Type"],
        y=by_type["Outstanding"],
        marker_color=PALETTE["teal"],
    )
    fig_type.update_layout(
        barmode="group",
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Amount (KSh)",
        xaxis_title="",
        legend=dict(orientation="h", y=1.12, x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_type, use_container_width=True)

with chart_row1_right:
    st.markdown("#### Loan Distribution by Status")
    status_data = filtered.groupby("Status", as_index=False).size()
    fig_status = px.pie(
        status_data,
        names="Status",
        values="size",
        hole=0.55,
        color_discrete_sequence=[
            PALETTE["green"],
            PALETTE["primary"],
            PALETTE["amber"],
            PALETTE["rose"],
            PALETTE["purple"],
        ],
    )
    fig_status.update_traces(textposition="inside", textinfo="percent+label", pull=[0.05, 0, 0, 0])
    fig_status.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_status, use_container_width=True)


chart_row2_left, chart_row2_right = st.columns(2)

with chart_row2_left:
    st.markdown("#### Outstanding Balance Concentration by Branch")
    by_branch = (
        filtered.groupby("Branch", as_index=False)["Outstanding Balance"]
        .sum()
        .sort_values("Outstanding Balance", ascending=True)
    )
    fig_branch = px.bar(
        by_branch,
        x="Outstanding Balance",
        y="Branch",
        orientation="h",
        text_auto=",.2f",
        color="Outstanding Balance",
        color_continuous_scale="Blues",
    )
    fig_branch.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Outstanding Balance (KSh)",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_branch, use_container_width=True)

with chart_row2_right:
    st.markdown("#### Portfolio Segmentation by Risk Rating")
    if "Risk Rating" in filtered.columns:
        risk_data = filtered.groupby("Risk Rating", as_index=False).size()
        fig_risk = px.pie(
            risk_data,
            names="Risk Rating",
            values="size",
            hole=0.55,
            color_discrete_sequence=[
                PALETTE["green"],
                PALETTE["teal"],
                PALETTE["amber"],
                PALETTE["rose"],
            ],
        )
        fig_risk.update_traces(textposition="inside", textinfo="percent+label")
        fig_risk.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("⚠️ Dataset does not contain a 'Risk Rating' column.")

st.divider()

# ----------------------------- Monthly Trend Timeline -----------------------------
st.subheader("📅 Monthly Disbursement Timeline & Volume")

monthly = (
    filtered.assign(Month=filtered["Disbursement Date"].dt.to_period("M").dt.to_timestamp())
    .groupby("Month", as_index=False)
    .agg(
        Principal=("Principal Amount", "sum"),
        Number_of_Loans=("Principal Amount", "size"),
    )
    .sort_values("Month")
)

fig_trend = go.Figure()
fig_trend.add_trace(
    go.Scatter(
        x=monthly["Month"],
        y=monthly["Principal"],
        name="Principal Disbursed (KSh)",
        mode="lines+markers",
        line=dict(color=PALETTE["teal"], width=3.5),
        fill="tozeroy",
        fillcolor="rgba(6, 182, 212, 0.08)",
        yaxis="y",
    )
)
fig_trend.add_trace(
    go.Bar(
        x=monthly["Month"],
        y=monthly["Number_of_Loans"],
        name="Loan Count",
        marker_color=PALETTE["indigo"],
        opacity=0.45,
        yaxis="y2",
    )
)
fig_trend.update_layout(
    height=410,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title="Timeline (Month)",
    yaxis=dict(title="Principal Amount (KSh)", side="left"),
    yaxis2=dict(title="Number of Loans", overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.12, x=0.01),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ----------------------------- Data Explorer & Export -----------------------------
st.subheader("🗂️ Filtered Loan Portfolio Inspector")
st.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** active records.")

column_configuration = {
    "Principal Amount": st.column_config.NumberColumn(format="KSh %,.2f"),
    "Outstanding Balance": st.column_config.NumberColumn(format="KSh %,.2f"),
    "Disbursement Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
}

if "Interest Rate (%)" in filtered.columns:
    column_configuration["Interest Rate (%)"] = st.column_config.NumberColumn(format="%.2f%%")

if "Credit Score" in filtered.columns:
    column_configuration["Credit Score"] = st.column_config.NumberColumn(format="%d")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
    column_config=column_configuration,
)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Filtered Records (CSV)",
    data=csv_bytes,
    file_name="filtered_loan_portfolio_executive.csv",
    mime="text/csv",
    type="primary",
)

st.caption(
    "💡 *PAR (Portfolio at Risk) is defined as the outstanding balance of loans in 'Overdue' or "
    "'Defaulted' status divided by total outstanding portfolio balance.*"
)