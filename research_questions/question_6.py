import streamlit as st
import pandas as pd
import time as t
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Research Question 2",
    layout="wide"
)

st.title("Bidding Zone Price Volatility")
st.write("Question: To what extent do countries with a higher share of renewables in their energy mix show greater electricity price volatility during extreme weather events compared to countries with a fossil-fuel-dominated mix?")

st.write("For this analysis we chose Finnland and Germany as representatives for the more renewable based countries due to their high share in installed reneable energy and Poland and Czechia as representatives for more fossil based \
        countires (ref.: Research Question 6). We define an extreme weather event here as the top 10 percent outliers when looking over all the data that happen over a prolonged period. For example is a Heatwave event defined by 3 consequtive days \
        that have a mean temperature in the top 10 percent of all days in Germany.")
#-----------------------------------------------------------
# Visual 1
#-----------------------------------------------------------

st.subheader("Price Volatility per Country and Weather Event")

st.write("First we where interested in how the Prices of the Bidding Zones of our selected countries react to extreme weather events over the years. When you view the different years, while we can see that extrem weather events can have a\
         substantial impact upon the price volatility, there is no clear pattern in the price volatility when comparing the years, countries and event types. Finnland seems to be the most apparent outlier here, since the Bidding Zone Price reacts \
         unusually strong to low wind events with a up to 85% deviation from its ususal volatility.")

df_volatility = pd.read_csv("./data/Q6_Data/Price_Volatility_Renewshare_Month.csv")

event_names = {
    "high_heat": "Heatwave",
    "low_wind" : "Low Wind Speed",
    "low_solar": "Low Solar Radiation",
    "low_soil": "Drought"
}
df_volatility["event_name"] = df_volatility["event_type"].map(event_names)

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

if (selected_event == []) or (selected_year == []):
    st.info("Please select atleast one weather event type and one year!")
else:
    df_volatility_filtered = df_volatility[(df_volatility["event_name"].isin(selected_event)) & (df_volatility["year"].isin(selected_year))]
    df_volatility_filtered_agg = df_volatility_filtered.groupby(["country","event_name"])["price_std_mean_diff_percentage"].agg("mean").reset_index()

    fig1, ax1 = plt.subplots(figsize=(10, 6))

    plot_data = df_volatility_filtered_agg.pivot(
        index="country",
        columns="event_name",
        values="price_std_mean_diff_percentage"
    )

    plot_data.plot(
        kind="bar",
        ax=ax1,
        width=0.8
    )

    ax1.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax1.axhline(0, color="black", linewidth=0.8)

    ax1.set_xlabel("Country", fontsize=14)
    ax1.set_ylabel("Change in price volatility (%)", fontsize=14)
    ax1.set_title("Price Volatility During Extreme Weather Events", fontsize=14)

    ax1.tick_params(
        axis="both"
        ,labelsize=14)

    ax1.grid(
        True,
        axis="both",
        linestyle="--",
        linewidth=0.6,
        alpha=0.7
    )

    ax1.legend(
        title="Event Type"
        ,fontsize=14
        ,title_fontsize=15
        ,bbox_to_anchor=(1, 1)
        ,loc="upper left"
    )

    plt.tight_layout()

    st.pyplot(fig1)

#-----------------------------------------------------------
# Visual 2
#-----------------------------------------------------------

st.subheader("Price Volatility against Renewable Share for each Weather Event")

st.write("For the next Visualisation we where interested in the actual connection between the Change in Price Volatility to a 'normal' day and the Total Renewable Generation Share during those events. What we found is, that\
        an extrem weather event doesnt necessearily ensure a higher price volatility for countries that are more reliant on renwable energy then fossil based once. But it can be seen, that countries with a higher renewable share have a potentially larger range \
         for their price volatility. While they are mostly in the same range as fossil based countries, they are also the once experiencing the highest peaks in price volatility.")

df_volatility_renew = pd.read_csv("./data/Q6_Data/Price_Volatility_Renewshare_Test.csv")

df_volatility_renew["event_name"] = df_volatility_renew["event_type"].map(event_names)

event_type_renew = df_volatility_renew["event_name"].unique()
renew_year = df_volatility_renew["year"].unique()

selected_event2 = st.selectbox(
    "Select weather event type:"
    ,options = event_type_renew
)   

selected_year2 = st.multiselect(
    "Select year:"
    ,options = renew_year
    ,default = [2019,2020,2021,2022,2023,2024]
    ,key="year_filter_plot2"
)   

plot_df2 = df_volatility_renew[(df_volatility_renew["event_name"] == selected_event2) & (df_volatility_renew["year"].isin(selected_year2))]

country_names = {
    "CZ": "Czechia",
    "DE": "Germany",
    "FI": "Finland",
    "PL": "Poland"
}

if selected_year2 == []:
    st.info("Please select atleast one year!")
else:
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    # Ein Scatter pro Land
    for country, group in plot_df2.groupby("country"):
        ax2.scatter(
            group["renew_share"],
            group["price_std_mean_diff_percentage"],
            label=country_names[country],
            alpha=0.7,
            s=50
        )

    # Null-Linie x
    ax2.axhline(
        0,
        color="grey",
        linestyle="--",
        linewidth=1
    )

    # Null-Linie y
    ax2.axvline(
        0,
        color="grey",
        linestyle="--",
        linewidth=1
    )


    ax2.set_xlabel("Total Renewable Generation Share (%)", fontsize=14)
    ax2.set_ylabel("Change in Price Volatility (%)", fontsize=14)
    ax2.set_title(
        f"Change in Price Variability against Total Renewable Generation Share"
        , fontsize=14
    )

    ax2.tick_params(
        axis="both"
        ,labelsize=14)

    ax2.grid(
        True,
        axis="both",
        linestyle="--",
        linewidth=0.6,
        alpha=0.7
    )

    ax2.legend(
        title="Countries"
        ,fontsize=14
        ,title_fontsize=15
        ,bbox_to_anchor=(1, 1)
        ,loc="upper left"
    )

    plt.tight_layout()
    st.pyplot(fig2)

#-----------------------------------------------------------
# Visual 3
#-----------------------------------------------------------

st.subheader("Curious Effekt of Seasons on the Price Volatility after the Energycrisis")

st.write("During our Datarefinment we made an interesting discovery. Before the Energycrisis of 2022, the price volatitly was pretty stable. But after the Energycrisis from 2023 onward, we can observe that the Price Volatility \
         suddenly seems to be linked to the seasons for some of the countries. The seasons are shown here by the maximum temperature over the years. While we are not sure why that is, we theorize that this could be due to missing imports from earlier trade partners which guarenteed \
         a stable supply of electricity or resources before 2022.")

df_volatility_country = pd.read_csv("./data/Q6_Data/Price_Volatitily_with_weather.csv")

country_names = {
    "FI": "Finland",
    "DE" : "Germany",
    "CZ": "Czechia",
    "PL": "Poland"
}
df_volatility_country["country_name"] = df_volatility_country["country"].map(country_names)

country = df_volatility_country["country_name"].unique()

selected_country = st.selectbox(
    "Country:"
    ,options = country
)   

df_volatility_country_filtered = df_volatility_country[df_volatility_country["country_name"] == selected_country]
df_volatility_country_filtered["date"] = pd.to_datetime(df_volatility_country_filtered["date"])

import matplotlib.dates as mdates

fig3, ax3 = plt.subplots(figsize=(10, 6))

ax3.plot(
    df_volatility_country_filtered["date"],
    df_volatility_country_filtered["price_std"],
    label="Price Volatility in Euro"
)

ax3.plot(
    df_volatility_country_filtered["date"],
    df_volatility_country_filtered["temperature_2m_max"],
    label="Max. Temperature in °C",
    color="orange"
)

ax3.set_xlabel("Date")
ax3.set_ylabel("Value")

ax3.legend()
ax3.grid(
    True,
    linestyle="--",
    linewidth=0.5,
    alpha=0.4
)

plt.tight_layout()
st.pyplot(fig3)