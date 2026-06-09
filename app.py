import streamlit as st
from filters import load_data, apply_filters
import charts as ch

# ── Page setup ─────────────────────────────────────────
st.set_page_config(
    page_title="⚡ Power Dashboard",
    page_icon="⚡",
    layout="wide"
)

# ── Professional dark theme CSS ────────────────────────
st.markdown("""
<style>
/* Dark background */
.stApp {
    background-color: #0A0E1A;
    color: #E2E8F0;
}

/* Sidebar dark */
section[data-testid="stSidebar"] {
    background-color: #080C16;
    border-right: 2px solid #1E2A3A;
}

/* KPI card style */
.kpi-card {
    background: linear-gradient(135deg, #111827, #1a2332);
    border: 1px solid #1E2A3A;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 4px;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #00B4D8;
}
.kpi-label {
    font-size: 0.75rem;
    color: #90A4AE;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}

/* Section headers */
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #00B4D8;
    border-left: 3px solid #00B4D8;
    padding-left: 10px;
    margin: 20px 0 10px 0;
}

/* Dashboard title */
.dash-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #E2E8F0;
}
.dash-sub {
    color: #90A4AE;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data("data/household_power_consumption.txt")

df_full = get_data()


# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ POWER DASHBOARD")
    st.markdown("---")

    # 1. Date range filter
    st.markdown("**📅 Date Range**")
    min_date = df_full["Datetime"].dt.date.min()
    max_date = df_full["Datetime"].dt.date.max()
    date_range = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # 2. Year filter
    st.markdown("**📆 Year**")
    all_years = sorted(df_full["Year"].unique().tolist())
    year_filter = st.multiselect(
        "Select year(s)",
        options=all_years,
        default=all_years
    )

    # 3. Season filter
    st.markdown("**🍂 Season**")
    season_filter = st.multiselect(
        "Select season(s)",
        options=["Spring", "Summer", "Autumn", "Winter"],
        default=["Spring", "Summer", "Autumn", "Winter"]
    )

    # 4. Hour slider
    st.markdown("**🕐 Hour of Day**")
    hour_range = st.slider(
        "Range", min_value=0, max_value=23, value=(0, 23)
    )

    # 5. Power slider
    st.markdown("**⚡ Active Power (kW)**")
    power_min = float(df_full["Global_active_power"].min())
    power_max = float(df_full["Global_active_power"].max())
    power_range = st.slider(
        "Range",
        min_value=power_min,
        max_value=power_max,
        value=(power_min, power_max),
        step=0.1
    )

    # 6. Weekday filter
    st.markdown("**📅 Weekday**")
    weekdays = ["Monday","Tuesday","Wednesday",
                "Thursday","Friday","Saturday","Sunday"]
    weekday_filter = st.multiselect(
        "Select day(s)",
        options=weekdays,
        default=weekdays
    )

    # 7. Text search
    st.markdown("**🔍 Text Search**")
    search_text = st.text_input(
        "Season / Weekday / Month",
        placeholder="e.g. Winter, Monday, Jan"
    )

    st.markdown("---")

    # 8. Reset button
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()


# ── Apply filters ──────────────────────────────────────
dr = date_range if isinstance(date_range, (list, tuple)) and len(date_range) == 2 else None

df = apply_filters(
    df_full,
    date_range=dr,
    year_filter=year_filter,
    season_filter=season_filter,
    hour_range=hour_range,
    power_range=power_range,
    weekday_filter=weekday_filter,
)

# Text search
if search_text.strip():
    q = search_text.strip().lower()
    mask = (
        df["Season"].str.lower().str.contains(q, na=False) |
        df["Weekday"].str.lower().str.contains(q, na=False) |
        df["Month_Name"].str.lower().str.contains(q, na=False)
    )
    df = df[mask]


# ── Header ─────────────────────────────────────────────
st.markdown(
    '<p class="dash-title">⚡ Household Electric Power Consumption</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="dash-sub">Interactive EDA Dashboard &nbsp;|&nbsp; '
    'Dec 2006 – Nov 2010 &nbsp;|&nbsp; Minute-level readings</p>',
    unsafe_allow_html=True
)
st.markdown("---")

if len(df) == 0:
    st.warning("⚠️ No data matches your filters. Please adjust.")
    st.stop()


# ── KPI Cards ──────────────────────────────────────────
st.markdown('<p class="section-title">📊 KEY METRICS</p>',
            unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

kpis = [
    (k1, f"{len(df):,}",                               "Total Records"),
    (k2, f"{df['Global_active_power'].mean():.2f} kW",  "Avg Active Power"),
    (k3, f"{df['Voltage'].mean():.1f} V",               "Avg Voltage"),
    (k4, f"{df['Global_intensity'].mean():.2f} A",      "Avg Intensity"),
    (k5, f"{df['Global_active_power'].max():.2f} kW",   "Peak Power"),
    (k6, f"{df['Global_active_power'].sum()/60:,.0f} kWh", "Total Energy"),
]

for col, value, label in kpis:
    with col:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)


# ── Row 1: Line + Bar ──────────────────────────────────
st.markdown('<p class="section-title">📈 TIME & TRENDS</p>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.pyplot(ch.chart_line_monthly(df))
with col2:
    st.pyplot(ch.chart_bar_hourly(df))


# ── Row 2: Histogram + Scatter ─────────────────────────
st.markdown('<p class="section-title">📊 DISTRIBUTIONS & RELATIONSHIPS</p>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.pyplot(ch.chart_histogram(df))
with col2:
    st.pyplot(ch.chart_scatter(df))


# ── Row 3: Pie + Count ─────────────────────────────────
st.markdown('<p class="section-title">🥧 CATEGORICAL OVERVIEW</p>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.pyplot(ch.chart_pie_season(df))
with col2:
    st.pyplot(ch.chart_countplot_year(df))


# ── Row 4: Box + Violin ────────────────────────────────
st.markdown('<p class="section-title">📦 SPREAD & DENSITY</p>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.pyplot(ch.chart_boxplot_weekday(df))
with col2:
    st.pyplot(ch.chart_violin_season(df))


# ── Row 5: Area Chart ──────────────────────────────────
st.markdown('<p class="section-title">📐 SUB-METERING TRENDS</p>',
            unsafe_allow_html=True)
st.pyplot(ch.chart_area_submetering(df))


# ── Row 6: Heatmap ─────────────────────────────────────
st.markdown('<p class="section-title">🌡️ CORRELATION HEATMAP</p>',
            unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.pyplot(ch.chart_heatmap(df))
#bonus charts
st.markdown('<p class="section-title"> ✨ BONUS CHARTS</p>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Bubble Chart** - Power * Voltage * Intensity per hour")
    st.pyplot(ch.chart_bubble(df))
with col2:
    st.markdown("**Funnel Chart** - Acg Power by timeday")
    st.pyplot(ch.chart_funnel(df))
    #st.pyplot(ch.chart_pairplot(df))
    st.markdown("**Pair Plot** - Relationships between key features by season")
with st.spinner("Rendring pair plot..."):
    st.pyplot(ch.chart_pairplot(df))


# ── Footer ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="color:#4A5568; font-size:0.75rem; text-align:center;">'
    '⚡ Household Power Dashboard &nbsp;|&nbsp; '
    'EDA Course &nbsp;|&nbsp; Instructor: Ali Hassan Sherazi'
    '</p>',
    unsafe_allow_html=True
)