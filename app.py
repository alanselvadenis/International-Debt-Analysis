import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Page setup
st.set_page_config(page_title="International Debt Analytics", layout="wide")

# Database Connection Credentials
DB_USER = "root"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "international_debt_db"

@st.cache_data
def get_data(query):
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    return pd.read_sql(query, engine)

# Header
st.title("🌐 International Debt Analysis Dashboard")
st.markdown("Visualizing historical global debt distributions, indicator breakdown, and country statistics.")

# Fetch high-level aggregated metrics directly from SQL
kpi_data = get_data("""
    SELECT 
        SUM(debt) as total_debt,
        COUNT(DISTINCT country_code) as total_countries,
        COUNT(DISTINCT indicator_code) as total_indicators
    FROM international_debt
""")

# Fetch aggregated country & indicator data for visualizations
df_agg = get_data("""
    SELECT c.country_name, i.indicator_name, SUM(d.debt) as total_debt 
    FROM international_debt d
    JOIN countries c ON d.country_code = c.country_code
    JOIN indicators i ON d.indicator_code = i.indicator_code
    GROUP BY c.country_name, i.indicator_name
""")

# Top KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Historical Global Debt", f"${kpi_data['total_debt'][0]:,.2f}")
col2.metric("Total Countries", kpi_data['total_countries'][0])
col3.metric("Total Indicators", kpi_data['total_indicators'][0])

st.divider()

# Sidebar Filter
selected_country = st.sidebar.multiselect(
    "Filter by Country:", 
    options=df_agg["country_name"].unique(), 
    default=df_agg["country_name"].unique()[:5]
)

filtered_df = df_agg[df_agg["country_name"].isin(selected_country)]

# Charts
st.markdown("**Top 10 Indebted Countries**")
top_countries_df = df_agg.groupby("country_name")["total_debt"].sum().reset_index().sort_values(by="total_debt", ascending=False).head(10)
fig_bar = px.bar(top_countries_df, x="country_name", y="total_debt", title="Top 10 Countries by Total Historical Debt", color="total_debt", color_continuous_scale="Reds")
st.plotly_chart(fig_bar, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Debt Indicator Breakdown (Filtered)**")
    indicator_df = filtered_df.groupby("indicator_name")["total_debt"].sum().reset_index().sort_values(by="total_debt", ascending=False).head(7)
    fig_pie = px.pie(indicator_df, names="indicator_name", values="total_debt", title="Top Debt Indicators")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("**Filtered Debt Data Table**")
    st.dataframe(filtered_df, height=350)