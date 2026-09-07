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

st.title("Research Question 3")
st.write(
"How is renewable electricity generation associated with regional meteorological conditions between Northern and Southern European countries?​"
)

st.subheader("Context")
st.markdown(
"This research question concerns itself with the relationship between renewable electricity generation and regional meteorological condition in Northern and Southern European Countries, which were aggregated into said regions based on their geographical location."
)

st.header("A look at the Data")
st.markdown(
"This section provides a visual overview of the data required to answer the research question. It comprises of two main components: Weather Data and Renewable Energy Generation Data. Each of them is fetched from 18 different countries in Europe, between 2023 and 2025, and the data is aggregated into the two relevant regions: Northern Europe and Southern Europe."
)

#============================

st.subheader("Weather Data")
st.markdown(
"The first component is the weather data, which consists of the weighted average of meteorological conditions across select representative coordinate clusters of countries in each region.  " 
"\nHere you can select a specific weather variable to visualize its trend over time, and adjust the date range to focus on specific periods."
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
        fig_weather.add_trace(go.Scatter(
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

st.subheader("Renewable Energy Generation Data")
st.markdown(
"The second component is then used to calculate the daily capacity factor of each region, for each technology. This is done to normalize the data, since energy production can differf significantly in scale between the two regions.  " 
"\nThe capacity factor is then calculated as the ratio of the energy generation data, and the capacity data.  " 
"\nFor these visualizations, you can select a specific technology, and then choose to view the data either at the regional level, or at the country level. If you select the country level, you can then choose which countries to include in the visualization. Alongside the graph, the capacity data is displayed in a table just below."
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
        fig_gen.add_trace(go.Scatter(
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
    
# Construct the Plotly Table
fig_table = go.Figure(data=[go.Table(
    header=dict(
        values=[f"<b>{col}</b>" for col in table_df.columns],
        fill_color='rgba(0,0,0,0)',  # Fully transparent background
        line_color='rgba(255,255,255,0.2)',  # Subtle translucent white borders
        align='left',
        font=dict(color='white', size=14)
    ),
    cells=dict(
        values=[table_df[col] for col in table_df.columns],
        fill_color='rgba(0,0,0,0)',  # Fully transparent background
        line_color='rgba(255,255,255,0.2)',  # Subtle translucent white borders
        align='left',
        font=dict(color='white', size=12),  # Flipped to white for the dark theme
        height=30
    )
)])

# Table Formatting
fig_table.update_layout(
    title=dict(text=f"<b>Total Capacity ({view_level} View)</b>", font=dict(color='white', size=20)),
    margin=dict(l=0, r=0, t=50, b=0),
    height=250,
    paper_bgcolor='rgba(0,0,0,0)',  # Makes the surrounding canvas transparent
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_table, use_container_width=True)

