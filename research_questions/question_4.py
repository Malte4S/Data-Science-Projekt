# AI-assisted code
# Used to help create the interactive part of the visualization.
# Bar chart generated with ChatGPT and adapted by the authors.

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Research Question 4",
    layout="wide"
)

st.title("Research Question 4")
st.write("Question: In drought years, do countries with high hydro dependency show a statistically significant increase in fossil fuel backup generation compared to countries with a diversified energy mix?")

df = pd.read_csv("./data/drought_energy_clean.csv")

st.subheader("Interactive Bubble Chart")
st.markdown(
    "Each country appears as one bubble, positioned by its overall mean "
    "hydro and fossil shares. Bubble size shows how many drought years that "
    "country experienced."
)

threshold = st.slider(
    "Hydro dependency threshold (%) - countries at or above this mean hydro "
    "share are classified as 'High Hydro Dependency', all others as "
    "'Diversified'",
    min_value=10,
    max_value=80,
    value=40,
    step=5,
)

agg = (
    df.groupby("country")
    .agg(
        mean_hydro_share=("hydro_share", "mean"),
        mean_fossil_share=("fossil_share", "mean"),
        n_drought_years=("drought", "sum"),
        n_years=("year", "count"),
    )
    .reset_index()
)

agg["mean_hydro_share_pct"] = agg["mean_hydro_share"] * 100
agg["mean_fossil_share_pct"] = agg["mean_fossil_share"] * 100

agg["group"] = agg["mean_hydro_share_pct"].apply(
    lambda x: "High Hydro Dependency" if x >= threshold else "Diversified"
)

BASE_SIZE = 14
SIZE_PER_DROUGHT_YEAR = 4

def bubble_size(row):
    size = BASE_SIZE + row["n_drought_years"] * SIZE_PER_DROUGHT_YEAR
    if row["country"] == "Norway":
        size = size / 2
    return size

agg["bubble_size"] = agg.apply(bubble_size, axis=1)

fig = px.scatter(
    agg,
    x="mean_hydro_share_pct",
    y="mean_fossil_share_pct",
    color="group",
    size="bubble_size",
    size_max=32,
    hover_name="country",
    hover_data={
        "mean_hydro_share_pct": ":.1f",
        "mean_fossil_share_pct": ":.1f",
        "n_drought_years": True,
        "n_years": True,
        "bubble_size": False,
        "group": True,
    },
    color_discrete_map={
        "High Hydro Dependency": "#1f77b4",
        "Diversified": "#ff7f0e",
    },
    labels={
        "mean_hydro_share_pct": "Mean hydro share (%, overall)",
        "mean_fossil_share_pct": "Mean fossil share of generation (%)",
        "group": "Classification",
        "n_drought_years": "Drought years",
    },
    title=f"Fossil backup generation vs. hydro dependency (threshold: {threshold}%)",
)

fig.add_vline(
    x=threshold,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"{threshold}% threshold",
    annotation_position="top",
)

fig.update_layout(
    legend_title_text="",
    height=600,
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Bubble size: scales with the number of drought years the country "
    "experienced. Norway had no drought years, so its bubble size is halved to make it visible."
)

'''
Bar chart for showing drought vs. non-drought years by hydro-dependency group.
'''

st.title("Fossil Backup Generation")
st.subheader("Drought vs. Non-Drought Years by Hydro-Dependency Group")

df["fossil_pct"] = df["fossil_share"] * 100

hydro_mean = df.groupby("country")["hydro_share"].mean() * 100

group_map = hydro_mean.apply(
    lambda x: "High Hydro Dependency (>= 40%)"
    if x >= 40
    else "Diversified"
)

df["group"] = df["country"].map(group_map)

df["drought_label"] = df["drought"].map({
    True: "Drought",
    False: "Non-Drought"
})

summary = (
    df.groupby(["group", "drought_label"])["fossil_pct"]
    .mean()
    .reset_index()
)

st.write("### Mean Fossil Share")

summary_display = summary.copy()
summary_display["fossil_pct"] = summary_display["fossil_pct"].round(2)

summary_display = summary_display.rename(
    columns={
        "group": "Hydro Dependency Group",
        "drought_label": "Condition",
        "fossil_pct": "Mean Fossil Share (%)"
    }
)

st.dataframe(
    summary_display,
    use_container_width=True,
    hide_index=True
)

groups = [
    "Diversified",
    "High Hydro Dependency (>= 40%)"
]

conditions = [
    "Non-Drought",
    "Drought"
]

colors = {
    "Non-Drought": "#9fb8c9",
    "Drought": "#d9534f"
}

x = np.arange(len(groups))
width = 0.32


fig, ax = plt.subplots(
    figsize=(9, 6.5),
    dpi=150
)

fig.patch.set_facecolor("white")

for i, condition in enumerate(conditions):

    means = []

    for group in groups:

        value = summary[
            (summary["group"] == group) &
            (summary["drought_label"] == condition)
        ]["fossil_pct"]

        if len(value) > 0:
            means.append(value.iloc[0])
        else:
            means.append(0)

    offset = (i - 0.5) * width

    ax.bar(
        x + offset,
        means,
        width,
        color=colors[condition],
        label=condition,
        edgecolor="white",
        linewidth=0.8
    )

ax.set_xticks(x)

ax.set_xticklabels(
    groups,
    fontsize=11.5
)

ax.set_ylabel(
    "Mean Fossil Share of Generation (%)",
    fontsize=11
)

ax.set_title(
    "Fossil Backup Generation: Drought vs. Non-Drought Years\n"
    "by Hydro-Dependency Group",
    fontsize=13.5,
    fontweight="bold",
    pad=14
)

ax.legend(
    frameon=False,
    fontsize=10.5,
    loc="upper right"
)

ax.grid(
    True,
    axis="y",
    color="#eeeeee",
    linewidth=0.8
)

ax.set_axisbelow(True)

ax.set_ylim(0, 75)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

st.pyplot(
    fig,
    use_container_width=True
)