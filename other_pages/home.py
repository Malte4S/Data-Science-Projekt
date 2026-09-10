import streamlit as st

st.title("Welcome to the Website for the Data Science Project: Energy Sector and Weather Events​​")
st.write("In recent history, we have been able to observe an increase in the frequency of extreme weather events due to climate change, such as heatwaves and droughts. \
         At the same time, countries all over the world have transitioned further and further towards renewable energy sources such as solar or wind power. \
         These energy sources are very dependent on weather conditions, and with the weather becoming more volatile, the question arises as to how meteorological conditions impact renewable power sources. \
         This project seeks to answer some of those questions by looking at power generation across multiple energy types and weather events over multiple years and regions.")
st.write("The data for this project was mainly sourced from the Open-Meteo API (weather) and the Energy-Charts API (energy). By using the navigation menu on the left, \
         you will find multiple pages that each contain information, findings, and visualisations for the six research questions we set out to answer.")
st.subheader("Sources")
st.text("        Energy-Charts Api (https://api.energy-charts.info/)\n\
        Open-Meteo Api (https://open-meteo.com/en/docs)")
st.write("Additional Sources:")
st.text("        Global Wind Atlas (https://globalwindatlas.info/en/download/gis-files)​\n\
        Our World in Data (https://ourworldindata.org)​​\n\
        World Bank Open Data​​ (https://data360.worldbank.org/en/api )\n\
        Global Energy Monitor (https://globalenergymonitor.org/download-data)​")