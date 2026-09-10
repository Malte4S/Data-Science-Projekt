# AI-assisted code
# Used to help create the interactive parts of the visualization.
# Bar chart generated with ChatGPT and adapted by the authors.

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(
    page_title="Research Question 4",
    layout="wide"
)

st.title("Research Question 4")
st.write("Question: In drought years, do countries with high hydro dependency show a statistically significant increase in fossil fuel backup generation compared to countries with a diversified energy mix?")

st.write(
    "For this analysis we use 14 countries (AUT, BRA, CAN, CHE, DEU, ESP, FRA "
    "GBR, ITA, NLD, NOR, PRT, SWE, USA). A country is classified as 'High Hydro "
    "Dependency' if its mean hydro share of electricity generation across the "
    "full period is at or above a chosen threshold (40% by default, adjustable "
    "in the first chart below), and 'Diversified' otherwise. A drought year is "
    "defined using the SPEI-12 (12-month Standardised Precipitation-Evapotranspiration "
    "Index). A year counts as a drought year when SPEI-12 falls below -1.0 " 
    "This threshold follows the standard drought classification used in climate "
    "research (McKee et al., 1993), where SPEI values between 0 and -0.99 are "
    "considered near normal, -1.0 to -1.49 moderately dry, -1.5 to -1.99 severely "
    "dry, and values at or below -2.0 extremely dry. "
)

df = pd.read_csv("./data/Q4_Data/drought_energy_clean.csv")

st.subheader("Bubble Chart")
st.markdown(
    "First we take a look at how each country's overall energy mix "
    "relates to how often it experienced drought. Each bubble below is one "
    "country, positioned by its overall mean hydro and fossil shares, with "
    "bubble size showing how many drought years that country experienced. "
)

threshold = st.slider(
    "Hydro dependency threshold (%): countries at or above this mean hydro "
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

fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.1)", showline=True, linewidth=2, linecolor="black", mirror=True)
fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.1)", showline=True, linewidth=2, linecolor="black", mirror=True)

fig.update_layout(
    legend_title_text="",
    height=600,
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True, key="bubble_chart")

st.caption(
    "Bubble size: scales with the number of drought years the country "
    "experienced. Norway had no drought years, so its bubble size is halved to make it visible."
)

'''
Bar chart for showing drought vs. non-drought years by hydro-dependency group.
'''

st.title("Fossil Backup Generation")
st.subheader("Drought vs. Non-Drought Years by Hydro-Dependency Group")
st.markdown(
    "Next we wanted to isolate the actual effect we are testing: does fossil "
    "fuel generation increase specifically in drought years, and does that "
    "increase look different for hydro-dependent countries compared to "
    "diversified ones? Here we fix the hydro dependency split at the 40% "
    "threshold and compare the mean fossil fuel share of generation across "
    "four groups: diversified countries in normal years, diversified "
    "countries in drought years, high-hydro-dependency countries in normal "
    "years, and high-hydro-dependency countries in drought years. If our "
    "hypothesis holds, the increase from normal to drought years should be "
    "larger for the High Hydro Dependency group than for the Diversified "
    "group."
)

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
    axis="both",
    color="#dddddd",
    linewidth=0.8
)

ax.set_axisbelow(True)

ax.set_ylim(0, 75)

for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(True)
    ax.spines[spine].set_color("black")
    ax.spines[spine].set_linewidth(1.2)

st.pyplot(
    fig,
    use_container_width=True
)

'''
Time series per country: hydro vs. fossil share, with drought years highlighted.
'''

HYDRO_COLOR = "#1F6F8B"
FOSSIL_COLOR = "#B5562E"
DROUGHT_BAND_COLOR = "rgba(217, 199, 154, 0.55)"
DROUGHT_THRESHOLD = -1.0

def drought_bands(rows):
    """Groups consecutive drought years into bands for shading."""
    bands = []
    start = None
    prev_year = None
    for _, r in rows.iterrows():
        if r["drought"]:
            if start is None:
                start = r["year"]
        elif start is not None:
            bands.append((start, prev_year))
            start = None
        prev_year = r["year"]
    if start is not None:
        bands.append((start, prev_year))
    return bands

def pct(x):
    return f"{x * 100:.1f}%"

st.title("Where Does the Electricity Come From When Drought Hits?")
st.subheader("Time Series by Country")
st.markdown(
    "Finally, the aggregated view above hides how drought and fossil "
    "generation actually unfold year by year within a single country, and it "
    "cannot show whether a country's response changed over time or was "
    "driven by one particularly bad drought. Here you can pick any country "
    "and see its hydro and fossil fuel share plotted year by year from "
    "2005-2023, with drought years (SPEI-12 < -1.0) shaded in the "
    "background. This makes it possible to check, for a specific country, "
    "whether fossil share visibly rises during the shaded drought periods, "
    "and whether that pattern looks different for hydro-heavy countries "
    "(marked with a ~) compared to diversified ones."
)

countries = sorted(df["country"].unique())

mean_hydro_by_country = df.groupby("country")["hydro_share"].mean()
hydro_heavy = set(mean_hydro_by_country[mean_hydro_by_country >= 0.40].index)

default_index = countries.index("Norway") if "Norway" in countries else 0
country_selected = st.selectbox(
    "Select country",
    countries,
    index=default_index,
    format_func=lambda c: f"{c} ~" if c in hydro_heavy else c,
    key="timeseries_country_select",
)
st.caption("~ = hydro plays a larger role here (>= 40% mean share)")

rows = df[df["country"] == country_selected].sort_values("year").reset_index(drop=True)
bands = drought_bands(rows)

fig_ts = go.Figure()

for start, end in bands:
    fig_ts.add_vrect(
        x0=start - 0.5,
        x1=end + 0.5,
        fillcolor=DROUGHT_BAND_COLOR,
        line_width=0,
        layer="below",
    )

fig_ts.add_trace(
    go.Scatter(
        x=rows["year"],
        y=rows["hydro_share"],
        mode="lines+markers",
        name="Hydro",
        line=dict(color=HYDRO_COLOR, width=2.5),
        marker=dict(size=6),
        customdata=rows[["spei_12", "drought"]],
        hovertemplate=(
            "Year %{x}<br>Hydro: %{y:.1%}<br>SPEI-12: %{customdata[0]:.2f}<extra></extra>"
        ),
    )
)

fig_ts.add_trace(
    go.Scatter(
        x=rows["year"],
        y=rows["fossil_share"],
        mode="lines+markers",
        name="Fossil (Coal+Gas+Oil)",
        line=dict(color=FOSSIL_COLOR, width=2.5),
        marker=dict(size=6),
        hovertemplate="Year %{x}<br>Fossil: %{y:.1%}<extra></extra>",
    )
)

fig_ts.update_layout(
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=10, r=10, t=40, b=10),
    height=420,
)

fig_ts.update_xaxes(title=None, dtick=1, showgrid=True, gridcolor="rgba(0,0,0,0.1)", showline=True, linewidth=2, linecolor="black", mirror=True)
fig_ts.update_yaxes(title=None, tickformat=".0%", showgrid=True, gridcolor="rgba(0,0,0,0.1)", showline=True, linewidth=2, linecolor="black", mirror=True)

st.plotly_chart(fig_ts, use_container_width=True, key="timeseries_chart")

drought_rows = rows[rows["drought"]]
normal_rows = rows[~rows["drought"]]

avg_hydro_drought = drought_rows["hydro_share"].mean() if len(drought_rows) else 0
avg_hydro_normal = normal_rows["hydro_share"].mean() if len(normal_rows) else 0
avg_fossil_drought = drought_rows["fossil_share"].mean() if len(drought_rows) else 0
avg_fossil_normal = normal_rows["fossil_share"].mean() if len(normal_rows) else 0

hydro_delta = avg_hydro_drought - avg_hydro_normal
fossil_delta = avg_fossil_drought - avg_fossil_normal

col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Hydro, Drought vs. Normal Years",
        f"{pct(avg_hydro_drought)}",
        f"{hydro_delta * 100:+.1f} pts vs. {pct(avg_hydro_normal)}",
    )
with col2:
    st.metric(
        "Fossil, Drought vs. Normal Years",
        f"{pct(avg_fossil_drought)}",
        f"{fossil_delta * 100:+.1f} pts vs. {pct(avg_fossil_normal)}",
        delta_color="inverse",
    )

st.caption(
    f"{len(drought_rows)} drought years - {len(normal_rows)} normal years in the dataset (2005-2023)"
)