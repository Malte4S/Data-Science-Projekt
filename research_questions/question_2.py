import streamlit as st
import pandas as pd
import time as t
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Research Question 6",
    layout="wide"
)
st.title("Power Generation Volatility and Power Trade Share")
st.write("Question: Has the growing share of weather-dependent renewable energy increased the volatility of national electricity generation during extreme weather events, \
         and to what extent do cross-border electricity imports mitigate this differently across countries?")

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

share_type = {
    "Solar Power" : "solar_share"
    ,"Wind Power" : "wind_share"
    ,"Water Power" : "water_share"
    ,"All Renewable Power types" : "renew_share"
}

generation_share= {
    "Solar Power" : "solar_generation_cv_mean_delta"
    ,"Wind Power" : "wind_generation_cv_mean_delta"
    ,"Water Power" : "water_generation_cv_mean_delta"
    ,"All Renewable Power types" : "total_generation_cv_mean_delta"
}

#-----------------------------------------------------------
# Visual 1
#-----------------------------------------------------------

st.subheader("Installed Generation Share per Country.")

st.write("In this visual we can see the develoment of the Installed Power in GigaWatts over the years. This should give you an idea about the actual fokus of the selected countries and help putting the following information into context.")

df_installed = pd.read_csv("./data/Q2_Data/installed_generation.csv")
df_installed["country_name"] = df_installed["country"].map(country_names)

country = df_installed["country_name"].unique()

selected_country = st.selectbox(
    "Country:"
    ,options = country
)   

df_installed_filtered = df_installed[df_installed["country_name"] == selected_country]

fig1, ax1 = plt.subplots(figsize=(10, 6))

df_installed_filtered.plot.area(
    x           = "year"
    ,y          = ["nuclear","water","wind","fossil","other","solar"]
    ,stacked    = True
    ,figsize    = (12, 6)
    ,alpha      = 0.7
    ,ax=ax1
)

ax1.legend(
    title           = "Power Type"
    ,fontsize       = 14
    ,title_fontsize = 15
    ,bbox_to_anchor = (1, 1)
    ,loc            = "upper left"
)

ax1.set_title(f"Energy production in {selected_country}")
ax1.set_xlabel("Year")
ax1.set_ylabel("Installed Power Production (GW)")

plt.tight_layout()
st.pyplot(fig1)

#-----------------------------------------------------------
# Visual 2
#-----------------------------------------------------------

st.subheader("Change in Generation Volatility against Renewable Share for each Weather Event and Technology Type.")

st.write("To answer the Research Question we have to take a look at the Change in Generation Volatility in relation to a 'normal' weather day in comparison to the actually installed Renewable Share. The renewable share autmatically adjusts \
         the Generation Volatility to the appropirat technology. We can see that especially wind and solar power react with a lower volatiltiy to a low wind/solar event. The effect seems to be dampend when the share of the given technology is rather small.\
         Heatwaves on the other hand seem to have an increasing effect when it comes to solar power as one might expect. Especially in countries with a high share in solar power are effected here.")

df_generation = pd.read_csv("./data/Q2_Data/Generation_data.csv")

df_generation["event_name"] = df_generation["event_type"].map(event_names)
df_generation["country_name"] = df_generation["country"].map(country_names)

event_type = df_generation["event_name"].unique()

selected_event2 = st.selectbox(
    "Select weather event type:"
    ,options    = event_type
    ,index      = 2
    ,key        = "event_filter_plot2"
)   

selected_share2 = st.selectbox(
    "Select renewable share type:"
    ,options = ["Solar Power", "Wind Power", "Water Power", "All Renewable Power types"]
    ,key="share_filter_plot2"
)   

df_generation_filtered = df_generation[(df_generation["event_name"] == selected_event2)]

fig2, ax2 = plt.subplots(figsize=(10, 6))

# Ein Scatter pro Land
for country, group in df_generation_filtered.groupby("country"):
    ax2.scatter(
        group[share_type[selected_share2]],
        group[generation_share[selected_share2]],
        label   = country_names[country],
        alpha   = 0.7,
        s       = 50
    )

# Null-Linie
ax2.axhline(
    0
    ,color       = "grey"
    ,linestyle   = "--"
    ,linewidth   = 1
)

ax2.axvline(
    0
    ,color       = "grey"
    ,linestyle   = "--"
    ,linewidth   = 1
)

ax2.set_xlabel(f"Installed Share - {selected_share2} (%)", fontsize=14)
ax2.set_ylabel(f"Change in Generation Volatility - {selected_share2} (%)", fontsize=14)
ax2.set_title(
    f"Change in Generation Volatility during {selected_event2} period"
    , fontsize = 14
)

ax2.tick_params(
    axis        = "both"
    ,labelsize  = 14)

ax2.grid(
    True
    ,axis        = "both"
    ,linestyle   = "--"
    ,linewidth   = 0.6
    ,alpha       = 0.7
)

ax2.legend(
    title           = "Country"
    ,fontsize       = 14
    ,title_fontsize = 15
    ,bbox_to_anchor = (1, 1)
    ,loc            = "upper left"
)

plt.tight_layout()
st.pyplot(fig2)

#-----------------------------------------------------------
# Visual 3
#-----------------------------------------------------------

st.subheader("Change in Trade Share against the Change in Generation Volatility for each Weather Event.")

st.write("In this last visual we can see the Change in trading share in relation to a 'normal' weather day in comparrison to the change in generation volatility in relation to a 'normal' weather day for a selected technology type. \
        As we can see, there does seem to be a correlation between the weather event selected and the Technology type. During a Low Solar Radiation Period we can see that the Solar Power generation Volatility as well as the Traiding share \
        Volatility in comparison to a 'normal' day drop, meaning that with the solar output becoming more stable (due to less being produced) the trading share becomes mroe stabel too. This makes sense since there is not as mcuh power to \
        trade in this situation thus there are not many chances to trade a lot of power. Similar trends can be observed for other technology types as well as, with water power being the exception, probably due to its small share in the total \
        power production for all countries.")

selected_event3 = st.selectbox(
    "Select weather event type:"
    ,options    = event_type
    ,index      = 2
    ,key        ="event_filter_plot3"
)   

selected_share3 = st.selectbox(
    "Select share type:"
    ,options =  ["Solar Power", "Wind Power", "Water Power", "All Renewable Power types"]
    ,key="share_filter_plot3"
)   

df_trade_filtered = df_generation[df_generation["event_name"] == selected_event3]

fig3, ax3 = plt.subplots(figsize=(10, 6))

# Ein Scatter pro Land
for country, group in df_trade_filtered.groupby("country"):
    ax3.scatter(
        group[generation_share[selected_share3]],
        group["traiding_share_delta"],
        label=country_names[country],
        alpha=0.7,
        s=50
    )

# Null-Linien
ax3.axhline(
    0,
    color="grey",
    linestyle="--",
    linewidth=1
)

ax3.axvline(
    0,
    color="grey",
    linestyle="--",
    linewidth=1
)

ax3.set_xlabel(f"Change in Generation Volatility - {selected_share3} (%)", fontsize=14)
ax3.set_ylabel("Change in Traiding Share (%)", fontsize=14)
ax3.set_title(
    f"Cross-Border Trade Response during {selected_event3} period"
    , fontsize=14
)

ax3.tick_params(
    axis="both"
    ,labelsize=14)

ax3.grid(
    True,
    axis="both",
    linestyle="--",
    linewidth=0.6,
    alpha=0.7
)

ax3.legend(
    title="Country"
    ,fontsize=14
    ,title_fontsize=15
    ,bbox_to_anchor=(1, 1)
    ,loc="upper left"
)

plt.tight_layout()
st.pyplot(fig3)
