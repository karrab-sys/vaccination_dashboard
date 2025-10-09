import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------
st.set_page_config(page_title="Vaccination vs Disease Trends Dashboard", layout="wide")

st.title("🌍 Vaccination vs Disease Trends Dashboard")
st.markdown("""
This interactive dashboard visualizes **Measles Vaccination Coverage (MCV1, MCV2)** 
and **Disease Incidence** using data from the **World Health Organization (WHO)** 
and **World Bank Population Indicators**.
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("merged_dataset.csv")
    df = df.dropna(subset=['COVERAGE', 'incidence_per_100k'])
    return df

merged = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

year_selected = st.sidebar.slider(
    "Select Year", int(merged["YEAR"].min()), int(merged["YEAR"].max()), 2020
)
country_selected = st.sidebar.selectbox(
    "Select Country", ["Global"] + sorted(merged["NAME"].dropna().unique().tolist())
)
antigen_selected = st.sidebar.selectbox("Select Vaccine", ["MCV1", "MCV2"])

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🌐 Global Trends", "📈 Country Trends", "🗺️ World Map"])

# --------------------------------------------------
# TAB 1: GLOBAL TRENDS
# --------------------------------------------------
with tab1:
    st.subheader("Global Measles Vaccination and Incidence Trends")

    global_cov = merged.groupby(['YEAR','ANTIGEN'])['COVERAGE'].mean().reset_index()
    fig1 = px.line(global_cov, x="YEAR", y="COVERAGE", color="ANTIGEN",
                   title="Global Measles Vaccination Coverage (MCV1 & MCV2)",
                   labels={"COVERAGE":"Coverage (%)", "YEAR":"Year", "ANTIGEN":"Vaccine Dose"})
    st.plotly_chart(fig1, use_container_width=True)

    global_inc = merged.groupby('YEAR')['incidence_per_100k'].mean().reset_index()
    fig2 = px.line(global_inc, x="YEAR", y="incidence_per_100k",
                   title="Global Measles Incidence per 100,000 Population",
                   labels={"YEAR":"Year", "incidence_per_100k":"Incidence per 100,000"})
    st.plotly_chart(fig2, use_container_width=True)

    avg = merged.groupby(['YEAR','ANTIGEN']).agg({'COVERAGE':'mean','incidence_per_100k':'mean'}).reset_index()
    fig3 = px.scatter(avg[avg['ANTIGEN']=="MCV1"], 
                      x="COVERAGE", y="incidence_per_100k", trendline="ols",
                      title="Coverage vs Incidence (MCV1)",
                      labels={"COVERAGE":"Coverage (%)","incidence_per_100k":"Incidence per 100,000"})
    st.plotly_chart(fig3, use_container_width=True)
    # Herd Immunity Threshold Visualization
subset = avg[avg['ANTIGEN']=="MCV1"]
fig4 = px.scatter(subset, x="COVERAGE", y="incidence_per_100k",
                  title="Herd Immunity Threshold (~95%)",
                  labels={"COVERAGE":"Coverage (%)", "incidence_per_100k":"Incidence per 100,000"})
fig4.add_vline(x=95, line_dash="dot", annotation_text="95% Threshold", annotation_position="top left")
st.plotly_chart(fig4, use_container_width=True)


# --------------------------------------------------
# TAB 2: COUNTRY TRENDS
# --------------------------------------------------
with tab2:
    st.subheader(f"{country_selected} – Vaccination vs Incidence Over Time")

    if country_selected == "Global":
        st.info("Select a specific country from the sidebar to view local trends.")
    else:
        subset = merged[(merged["NAME"]==country_selected) & (merged["ANTIGEN"]==antigen_selected)]

        if subset.empty:
            st.warning("No data available for this country and vaccine.")
        else:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=subset["YEAR"], y=subset["COVERAGE"], mode="lines+markers",
                name="Coverage (%)", line=dict(color="green")))
            fig4.add_trace(go.Scatter(
                x=subset["YEAR"], y=subset["incidence_per_100k"], mode="lines+markers",
                name="Incidence per 100,000", yaxis="y2", line=dict(color="red")))

            fig4.update_layout(
                title=f"{country_selected} – {antigen_selected} Coverage vs Incidence",
                xaxis=dict(title="Year"),
                yaxis=dict(title="Coverage (%)", color="green"),
                yaxis2=dict(title="Incidence per 100,000", overlaying="y", side="right", color="red")
            )
            st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------
# TAB 3: MAP VISUALIZATION
# --------------------------------------------------
with tab3:
    st.subheader(f"Global {antigen_selected} Coverage Map – {year_selected}")

    subset_map = merged[(merged["YEAR"]==year_selected) & (merged["ANTIGEN"]==antigen_selected)]
    fig5 = px.choropleth(subset_map, locations="CODE", color="COVERAGE",
                         hover_name="NAME", projection="natural earth",
                         color_continuous_scale="YlGn",
                         title=f"{antigen_selected} Coverage by Country – {year_selected}",
                         labels={"COVERAGE":"Coverage (%)"})
    st.plotly_chart(fig5, use_container_width=True)

    subset_map['Risk'] = subset_map['COVERAGE'].apply(lambda x: "High Risk" if x < 80 else "Low Risk")
    fig6 = px.choropleth(subset_map, locations="CODE", color="Risk",
                         hover_name="NAME", projection="natural earth",
                         title=f"Outbreak Risk Map – {year_selected}",
                         color_discrete_map={"High Risk":"red","Low Risk":"green"})
    st.plotly_chart(fig6, use_container_width=True)

# --------------------------------------------------
# ABOUT SECTION
# --------------------------------------------------
st.markdown("---")
st.markdown("""
### 📖 About This Project
**Course:** Graduate Capstone – Information Visualization  
**Student:** Bhavana Karra (G02533974)  
**Data Sources:**  
- [WHO Immunization Data Portal](https://immunizationdata.who.int/)  
- [World Bank Population Indicators](https://data.worldbank.org/indicator/SP.POP.TOTL)

**Objective:**  
To explore and visualize how global vaccination coverage relates to measles outbreaks, 
highlighting herd immunity thresholds and identifying high-risk countries.

---
""")

