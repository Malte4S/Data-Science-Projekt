import streamlit as st
import pandas as pd
import time as t
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Research Question 2",
    layout="wide"
)

st.title("Research Question 2")
st.write("Question: To what extent do countries with a higher share of renewables in their energy mix show greater electricity price volatility during extreme weather events compared to countries with a fossil-fuel-dominated mix? ")

df = pd.read_csv("./Price Volatility Analysis/test.csv")

st.subheader("Test Dataframe")
st.dataframe(df)

st.subheader("Test Visual")

df["date"] = pd.to_datetime(
        dict(
            year=df["year"],
            month=df["month"],
            day=1
        )
    )

countries = ["DE", "FI", "PL", "CZ"]
event = "weather_event"

fig, axes = plt.subplots(
    2, 2,
    figsize=(16, 10),
    sharex=True,
    sharey=True
)

axes = axes.flatten()

for ax, country in zip(axes, countries):

    data = df[
        df["country"] == country
    ].copy()

    data["date"] = pd.to_datetime(
        dict(
            year=data["year"],
            month=data["month"],
            day=1
        )
    )

    normal = data[data[event] == False]
    extreme = data[data[event] == True]

    # normale Tage
    ax.plot(
        normal["date"],
        normal["mean"],
        marker="o",
        markersize=3,
        label="Normal"
    )

    # Event-Tage
    ax.scatter(
        extreme["date"],
        extreme["mean"],
        s=50,
        label="Weather event",
        c="orange",
        zorder=3
    )

    ax.set_title(country)
    ax.grid(alpha=0.3)

fig.suptitle(
    "Price Volatility during Weather Events",
    fontsize=16
)

fig.supxlabel("Date")
fig.supylabel("Mean Daily Price Volatility [€/MWh]")

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="upper center",
    ncol=2
)

plt.tight_layout()
st.pyplot(fig)
