# Imports

import streamlit as st
import pandas as pd
import time as t
import matplotlib.pyplot as plt
import numpy as np

# Main Title and Research Question

st.set_page_config(
    page_title  = "Bidding Zone Price Volatility",
    layout      = "wide"
)

st.title("Bidding Zone Price Volatility")
st.write("Question: To what extent do countries with a higher share of renewables in their energy mix show greater electricity price volatility during extreme weather events compared to countries with a fossil-fuel-dominated mix?")

st.write("For this analysis we chose Finnland and Germany as representatives for the more renewable based countries due to their high share in installed reneable energy and Poland and Czechia as representatives for more fossil based \
        countires (ref.: Research Question 6). We define an extreme weather event here as the top 10 percent outliers when looking over all the data that happen over a prolonged period. For example is a Heatwave event defined by 3 consequtive days \
        that have a mean temperature in the top 10 percent of all days in Germany.")

# Explainaitions for Metrics that are used in the visuals

st.subheader("Key metrics")
st.write("__Price Volatility:__ The Price Volatility decribes how much the Price changes within a weather event period. Its Calculated as follows:")
st.latex(r'''\frac{\text{Standard deviation of the Price}}{\text{Mean of the Price}} \cdot 100''')
st.write("__Change in Price Volatility:__ Describes how the Price Volatiltiy of an Extreme Weather Event differs from the Price Volatility of 'normal' day.")
st.write("__Renewable Generation Share:__ The Renewable Generation Share shows how much of the Generated Energy during a weather event period was renewable. Its calculated as follows:")
st.latex(r'''\frac{\text{Mean of the Renewable Power Generation}}{\text{Total Power Generation}} \cdot 100''')

st.subheader("Whats a Bidding Zone?")
st.write("A Bidding Zone is a Region in which the same wholesale electricity price applies. Participants can trade electricity freely with in a Bidding Zone without considering the actual transmission rates of the power grid. A low Price means, that there is alot of electricity overhead that can be traded\
         while a high price reflects a lack of electricity to cover the demand. Trade between Bidding Zones will push the prices towards each other but only until the transmission rate between the networks is exhausted an no further electricity can be traded.")

# Translation-dictionaries for converting values into more readable data later

event_names = {
    "high_heat": "Heatwave"
    ,"low_wind" : "Low Wind Speed"
    ,"low_solar": "Low Solar Radiation"
    ,"low_soil": "Drought"
}

country_names = {
    "CZ": "Czechia"
    ,"DE": "Germany"
    ,"FI": "Finland"
    ,"PL": "Poland"
}

# Imports and applying translation dictionaries

# Visual 1 and 2
df_volatility = pd.read_csv("./data/BZPriceVolatility_Data/Price_Volatility_Renewshare.csv")
df_volatility["event_name"] = df_volatility["event_type"].map(event_names)

# Visual 3 
df_price_country = pd.read_csv("./data/BZPriceVolatility_Data/Price_Volatility_Overall.csv")
df_price_country["country_name"] = df_price_country["country"].map(country_names)

# date column was needed but had to be build, figured out with LLM
df_price_country["date"] = pd.to_datetime(
    dict(
        year    = df_price_country["year"]
        ,month  = df_price_country["month"]
        ,day    = df_price_country["day"]
        )
    )

#-----------------------------------------------------------
# Visual 1
#-----------------------------------------------------------

# Title and Explainaitions

st.subheader("Price Volatility per Country and Weather Event")

st.write("First we where interested in how the Prices of the Bidding Zones of our selected countries react to extreme weather events over the years. When you view the different years, while we can see that extrem weather events can have a\
         substantial impact upon the price volatility, there is no clear pattern in the price volatility when comparing the years, countries and event types. Finnland seems to be the most apparent outlier here, since the Bidding Zone Price reacts \
         unusually strong to low wind events with a up to 85% deviation from its ususal volatility.")

# Building the Selectors for weather event and year 

event_type = df_volatility["event_name"].unique()
year       = df_volatility["year"].unique()

selected_year = st.multiselect(
    "Select year:"
    ,options = year
    ,default = [2019,2020,2021,2022,2023,2024]
    ,key="year_filter_plot1"
)

selected_event = st.multiselect(
    "Select weather event type:"
    ,options = event_type
    ,default = ["Heatwave","Low Wind Speed","Low Solar Radiation","Drought"]
)   

# Plot is build, if atleast one year is selected

if (selected_event == []) or (selected_year == []):
    st.info("Please select atleast one weather event type and one year!")
else:

    # Filter data on selected values from selectors

    df_volatility_filtered = df_volatility[(df_volatility["event_name"].isin(selected_event)) & (df_volatility["year"].isin(selected_year))]
    df_volatility_filtered_agg = df_volatility_filtered.groupby(["country","event_name"])["price_std_mean_diff_percentage"].agg("mean").reset_index()

    # To figure out how to pivot the data and make it work for the plot LLM was used
    plot_data = df_volatility_filtered_agg.pivot(
        index       = "country"
        ,columns    = "event_name"
        ,values     = "price_std_mean_diff_percentage"
    )

    # Build Plot

    fig1, ax1 = plt.subplots(figsize=(10, 6))

    plot_data.plot(
        kind    = "bar"
        ,ax     = ax1
        ,width  = 0.8
    )

    # Labels, sizes and legend

    ax1.axhline(
        y           = 0
        ,color      = "black"
        ,linewidth  = 0.8
    )

    ax1.tick_params(
        axis        = "both"
        ,labelsize  = 14
    )

    ax1.grid(
        visible     = True
        ,axis       = "both"
        ,linestyle  = "--"
        ,linewidth  = 0.6
        ,alpha      = 0.7
    )

    ax1.legend(
        title           = "Event Type"
        ,fontsize       = 14
        ,title_fontsize = 15
        ,bbox_to_anchor = (1, 1)
        ,loc            = "upper left"
    )

    ax1.set_xlabel("Country", fontsize=14)
    ax1.set_ylabel("Change in price volatility (%)", fontsize=14)
    ax1.set_title("Price Volatility During Extreme Weather Events", fontsize=14)

    plt.tight_layout()
    st.pyplot(fig1)

#-----------------------------------------------------------
# Visual 2
#-----------------------------------------------------------

# Title and Explainaitions

st.subheader("Price Volatility against Renewable Share for each Weather Event")

st.write("For the next Visualisation we where interested in the actual connection between the Change in Price Volatility to a 'normal' day and the Total Renewable Generation Share during those events. What we found is, that\
        an extrem weather event doesnt necessearily ensure a higher price volatility for countries that are more reliant on renwable energy then fossil based once. But it can be seen, that countries with a higher renewable share have a potentially larger range \
         for their price volatility. While they are mostly in the same range as fossil based countries, they are also the once experiencing the highest peaks in price volatility.")

# Building the Selectors for weather event and years and apply filter

event_type2 = df_volatility["event_name"].unique()
year2       = df_volatility["year"].unique()

selected_event2 = st.selectbox(
    "Select weather event type:"
    ,options = event_type2
)   

selected_year2 = st.multiselect(
    "Select year:"
    ,options    = year2
    ,default    = [2019,2020,2021,2022,2023,2024]
    ,key        = "year_filter_plot2"
)   

plot_df2 = df_volatility[(df_volatility["event_name"] == selected_event2) & (df_volatility["year"].isin(selected_year2))]

# Plot is build, if atleast one year is selected

if selected_year2 == []:
    st.info("Please select atleast one year!")
else:

    # Build the Plot
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    # One Scatter per country, LLM used to figure out how to do multiplle scatter plots in one
    for country, group in plot_df2.groupby("country"):
        ax2.scatter(
            x       = group["renew_share"]
            ,y      = group["price_std_mean_diff_percentage"]
            ,label  = country_names[country]
            ,alpha  = 0.7
            ,s      = 50
        )

    # Labels, sizes legend, etc

    ax2.axhline(
        y           = 0
        ,color      = "grey"
        ,linestyle  = "--"
        ,linewidth  = 1
    )

    ax2.axvline(
        x           = 0
        ,color      = "grey"
        ,linestyle  = "--"
        ,linewidth  = 1
    )

    ax2.tick_params(
        axis        = "both"
        ,labelsize  = 14
    )

    ax2.grid(
        visible     = True
        ,axis       = "both"
        ,linestyle  = "--"
        ,linewidth  = 0.6
        ,alpha      = 0.7
    )

    ax2.legend(
        title           = "Countries"
        ,fontsize       = 14
        ,title_fontsize = 15
        ,bbox_to_anchor = (1, 1)
        ,loc            = "upper left"
    )

    ax2.set_xlabel("Total Renewable Generation Share (%)", fontsize=14)
    ax2.set_ylabel("Change in Price Volatility (%)", fontsize=14)
    ax2.set_title(
        f"Change in Price Variability against Total Renewable Generation Share"
        ,fontsize = 14
    )

    plt.tight_layout()
    st.pyplot(fig2)

#-----------------------------------------------------------
# Visual 3
#-----------------------------------------------------------

# Title and Explainaitions

st.subheader("Curious Effekt of Seasons on the Price Volatility after the Energycrisis")

st.write("During our Datarefinment we made an interesting discovery. Before the Energycrisis of 2022, the price volatitly was pretty stable. But after the Energycrisis from 2023 onward, we can observe that the Price Volatility \
         suddenly seems to be linked to the seasons for some of the countries. The seasons are shown here by the maximum temperature over the years. While we are not sure why that is, we theorize that this could be due to missing imports from earlier trade partners which guarenteed \
         a stable supply of electricity or resources before 2022.")

# Building the Selector for country and year and apply filter

country     = df_price_country["country_name"].unique()
price_year  = df_price_country["year"].unique()

selected_country = st.selectbox(
    "Country:"
    ,options = country
)   

selected_year3 = st.slider(
    "Select year range:"
    ,min_value  = 2019
    ,max_value  = 2024
    ,value      = (2019,2024)
    ,step       = 1
)

df_volatility_country_filtered = df_price_country[
    (df_price_country["country_name"] == selected_country)
    & (df_price_country["year"] >= selected_year3[0])
    & (df_price_country["year"] <= selected_year3[1])]

# Build Plots, LLM used to figure out how to put multiple plots in one chart

fig3, ax3 = plt.subplots(figsize=(10, 6))

ax3.plot(
    df_volatility_country_filtered["date"]
    ,df_volatility_country_filtered["price_std"]
    ,label = "Price Volatility in Euro"
)

ax3.plot(
    df_volatility_country_filtered["date"]
    ,df_volatility_country_filtered["temperature_daily_mean"]
    ,label = "Max. Temperature in °C"
    ,color = "orange"
)

# Labels, sizes legend, etc

ax3.legend()
ax3.grid(
    visible     = True
    ,linestyle  = "--"
    ,linewidth  = 0.6
    ,alpha      = 0.7
)

ax3.set_xlabel("Date")
ax3.set_ylabel("Value")
ax3.set_title(
    f"Change in Price Variability and the Max. Temeperatur to show the Seasons"
    ,fontsize = 14
)

plt.tight_layout()
st.pyplot(fig3)