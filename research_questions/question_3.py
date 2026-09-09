# AI assisted code used for graphing and plots.
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
import statsmodels.api as sm
from datetime import date


st.set_page_config(
    page_title="Research Question 3",
    layout="wide"
)

st.title("Effect of Weather Conditions on Renewable Energy Generation in Northern and Southern Europe")
st.write(
"This research question concerns itself with how renewable electricity generation is associated with regional meteorological conditions between Northern and Southern European countries.  "
"\nIn this section, we go over the methodology, take a look at some of the data used for the final visualization, and then take a look at the sandbox used to find the relevant correlations, before exploring those."
)

st.subheader("Methodology")
st.markdown(
"First we identified the relevant energy types, time frame, and countries we would consider for this analysis. In the end, we narrowed it down to four energy types, 18 countries from both regions (a list of which is available in the coming visualizations), and a time frame of 2023 to 2025. The following sources were utilized:  "
"\nOpen-Meteo API: This provided the relevant weather data for select variables, such as shortwave radition, or wind speed. For this specific question, the data was fetched from selected coordinate clusters to minimize API calls.  "
"\nEnergy Charts API: This provided energy generation as well as yearly capacity data for the selected countries, which was used to calculate the capacity factor.  "
"\nGlobal Energy Monitor: Lastly, this source provided the relevant locations and coordinates used to cluster and weight the relevant weather data per energy type."    
)

st.header("A Look at the Data")
st.markdown(
"Here we provide a visual overview of the aforementioned data required to answer the research question. It comprises of two main components: the weather data and the renewable energy generation data."
)

#============================

st.subheader("Regional Weighted Weather Data")
st.markdown(
"The first dataset is the weather data, which was fetched from 18 different countries across hundreds of unique coordinate clusters. These were then weighted acoording to that year's total capacity and aggregated into their regions.  "
"\nThe result represents the regional average weather, weighted by the spatial distribution of generation capacity across the entire time frame.  "
"\n**In this graph, you can select a specific weather variable to visualize its trend over time, and adjust the date range to focus on specific periods**"
)

target_weather_var = st.selectbox("Select a Weather Variable", ['Shortwave_Radiation_Sum', 'Wind_Speed_100m', 'Wind_Gusts_10m_Max', 'Temperature_2m_Max', 'Apparent_Temperature_Min', 'Precipitation_Sum', 'Snow_Depth'], index=0)

if "weather_date_range" not in st.session_state:
    st.session_state.weather_date_range = (date(2023, 1, 1), date(2025, 12, 31))

start_date, end_date = st.session_state.weather_date_range

# 1. Load and prep weather data
weather_timeseries = pd.read_csv("./data/Q3_Data/Regional_Weighted_Weather_2023_2025.csv")
weather_timeseries['Date'] = pd.to_datetime(weather_timeseries['Date'])

# 2. Apply Optional Timeframe Filter
weather_timeseries = weather_timeseries[weather_timeseries['Date'] >= pd.to_datetime(start_date)]
weather_timeseries = weather_timeseries[weather_timeseries['Date'] <= pd.to_datetime(end_date)]

fig_weather = go.Figure()
clean_var_name = target_weather_var.replace('_', ' ').title()
colors = {'Northern Europe': '#1f77b4', 'Southern Europe': '#ff7f0e'}

# 3. Generate a trace for each Region
for region in weather_timeseries['Region'].unique():
    region_data = weather_timeseries[weather_timeseries['Region'] == region]
    
    # Verify the variable exists to prevent fatal application crashes
    if target_weather_var in region_data.columns:
        fig_weather.add_trace(go.Scattergl(
            x=region_data['Date'],
            y=region_data[target_weather_var],
            mode='lines',
            name=region,
            line=dict(color=colors.get(region, 'gray')),
            visible=True, # Plotly natively allows toggling regions by clicking the legend
            hovertemplate=f"<b>{region}</b><br>Date: %{{x|%Y-%m-%d}}<br>{clean_var_name}: %{{y:.2f}}<extra></extra>"
        ))
        
# 4. Graph Formatting
fig_weather.update_layout(
    title=dict(text=f"<b>Regional Trends: {clean_var_name}</b>", font=dict(size=20)),
    xaxis_title=dict(text="Date", font=dict(size=14)),
    yaxis_title=dict(text=clean_var_name, font=dict(size=14)),
    template="plotly_white",
    hovermode="x unified", # Groups both regions together on hover for easy daily comparison
    legend=dict(
        title=dict(text="<b>Toggle Region</b>"),
        yanchor="top", y=1, xanchor="left", x=1.02,
        bgcolor="rgba(255,255,255,0.85)", bordercolor="black", borderwidth=1
    ),
    margin=dict(l=40, r=200, t=60, b=0)
)

fig_weather.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
fig_weather.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

st.plotly_chart(fig_weather, use_container_width=True)


_, middle, _  = st.columns([0.02, 0.7, 0.13], gap="small")

with middle:
    st.slider(label="Slide to select date range", min_value= date(2023, 1, 1), max_value= date(2025, 12, 31), value=(start_date, end_date), key="weather_date_range",format="DD/MM/YYYY")

#============================

st.subheader("Daily Capacity Factor")
st.markdown(
"To account for possibly significant difference in energy output between both regions, a capacity factor is calculated. For each technology, this is done by dividing the daily energy generation of each country by its theoretical capacity, then aggregating them into regions.  " 
"\n**You can select the specific technology, and then choose to view the data at the regional or country level. Alongside the graph, the capacity data is displayed in a table below.**"
)

active_tech = st.segmented_control("Select the Technology", ['Solar', 'Wind', 'Hydro', 'Bioenergy'], selection_mode="single", default='Solar', required=True, key="generation_data")
view_level = st.segmented_control("Select the View Level", ["Region", "Country"], selection_mode="single", default="Region", required=True)
if view_level == "Country":
    plot_entities = st.multiselect("Select Countries", ["Bosnia and Herzegovina", "Croatia", "Denmark", "Estonia", "Finland", "Greece", "Ireland", "Italy", "Latvia", "Lithuania", "Montenegro", "North Macedonia", "Norway", "Portugal", "Serbia", "Slovenia", "Spain", "Sweden"], default=None)
else:
    plot_entities = st.multiselect("Select Regions", ['Northern Europe', 'Southern Europe'], default=['Northern Europe', 'Southern Europe'])


# Load and prep generation data
gen_df = pd.read_csv("./data/Q3_Data/European_Daily_Generation_2023_2025.csv")
gen_df['Date'] = pd.to_datetime(gen_df['Date'])

fig_gen = go.Figure()

# Dynamically group based on UI selection
if view_level == "Region":
    plot_df = gen_df[gen_df['Region'].isin(plot_entities)]
    plot_df = plot_df.groupby(['Region', 'Date'])[active_tech].sum().reset_index()
    entity_col = 'Region'
else:
    plot_df = gen_df[gen_df['Country'].isin(plot_entities)]
    entity_col = 'Country'
    
# Generate a trace for every selected entity
for entity in plot_entities:
    entity_data = plot_df[plot_df[entity_col] == entity]
    
    if not entity_data.empty:
        # Force a continuous daily calendar to break lines on missing days
        entity_data = entity_data.set_index('Date').resample('D').asfreq().reset_index()
        fig_gen.add_trace(go.Scattergl(
            x=entity_data['Date'],
            y=entity_data[active_tech],
            mode='lines',
            name=entity,
            visible=True, # Plotly natively allows toggling by clicking the legend
            hovertemplate=f"<b>{entity}</b><br>Date: %{{x|%Y-%m-%d}}<br>Generation: %{{y:,.0f}} MWh<extra></extra>"
        ))

# Graph Formatting
fig_gen.update_layout(
    title=dict(text=f"<b>Daily {active_tech} Generation ({view_level} View)</b>", font=dict(size=20)),
    xaxis_title=dict(text="Date", font=dict(size=14)),
    yaxis_title=dict(text="Generation (MWh)", font=dict(size=14)),
    template="plotly_white",
    hovermode="x unified",
    legend=dict(
        title=dict(text="<b>Click to Toggle</b>"),
        yanchor="top", y=1, xanchor="left", x=1.02,
        bgcolor="rgba(255,255,255,0.85)", bordercolor="black", borderwidth=1
    ),
    margin=dict(l=40, r=200, t=60, b=40)
)

fig_gen.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
fig_gen.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

st.plotly_chart(fig_gen, use_container_width=True)


# Load capacity data
cap_df = pd.read_csv("./data/Q3_Data/European_Validated_Capacity_2023_2025.csv")

# Route logic based on view level
if view_level == "Region":
    table_df = cap_df[cap_df['Region'].isin(plot_entities)]
    table_df = table_df.groupby(['Region', 'Year'])[['Bioenergy', 'Hydro', 'Wind', 'Solar']].sum().reset_index()
else:
    table_df = cap_df[cap_df['Country'].isin(plot_entities)]
    table_df = table_df[['Region', 'Country', 'Year', 'Bioenergy', 'Hydro', 'Wind', 'Solar']]
    
# Format the raw numbers into readable text strings (e.g., "15,400 MW")
for col in ['Bioenergy', 'Hydro', 'Wind', 'Solar']:
    if col in table_df.columns:
        table_df[col] = table_df[col].apply(lambda x: f"{x:,.0f} MW")
    
# Display the capacity data using a native Streamlit dataframe
st.markdown(f"**Total Capacity ({view_level} View)**")
st.dataframe(table_df, use_container_width=True, hide_index=True)

