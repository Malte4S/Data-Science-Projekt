import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def load():
    df = pd.read_csv("data/Q5_Data/wind.csv")
    x = df["wind_speed_100m_mean_ms"].to_numpy()
    y = df["capacity_factor_pct"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    df["performance_score"] = y - (slope * x + intercept)

    return df


df = load()

# Sidebar controls
st.sidebar.header("Map settings")

color_choice = st.sidebar.radio(
    "Color countries by",
    options=["Capacity factor (%)", "Over-/Underperformance score"],
    index=0,
    key="wind_map_color_choice",
)

color_col = (
    "capacity_factor_pct"
    if color_choice == "Capacity factor (%)"
    else "performance_score"
)

color_scale = "RdBu" if color_col == "performance_score" else "YlGnBu"
color_midpoint = 0 if color_col == "performance_score" else None

# Main title
st.title("🌍 Global Wind Resource & Performance Map")
st.caption(
    "Capacity factor = actual generation ÷ theoretical max generation at full capacity. "
    "Performance score = actual capacity factor minus the capacity factor predicted "
    "from the country's mean wind speed alone (positive = overperforming its wind resource)."
)

fig = px.choropleth(
    df,
    locations="iso_code",
    color=color_col,
    hover_name="country",
    hover_data={
        "iso_code": False,
        "wind_speed_100m_mean_ms": ":.2f",
        "power_density_100m_mean_wm2": ":.0f",
        "wind_capacity_gw": ":.2f",
        "wind_generation_twh": ":.2f",
        color_col: ":.2f",
    },
    color_continuous_scale=color_scale,
    color_continuous_midpoint=color_midpoint,
    labels={
        "wind_speed_100m_mean_ms": "Mean wind speed (m/s, 100m)",
        "power_density_100m_mean_wm2": "Power density (W/m², 100m)",
        "wind_capacity_gw": "Installed capacity (GW)",
        "wind_generation_twh": "Generation (TWh)",
        "capacity_factor_pct": "Capacity factor (%)",
        "performance_score": "Performance score (pp)",
    },
    projection="natural earth",
)

fig.update_geos(showcountries=True, countrycolor="lightgray", showcoastlines=False)
fig.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    height=600,
    coloraxis_colorbar=dict(
        title="Capacity<br>factor (%)"
        if color_col == "capacity_factor_pct"
        else "Performance<br>score (pp)"
    ),
)

st.plotly_chart(fig, use_container_width=True)

st.header("Ranked Performance Residuals")
st.caption(
    "Regression of capacity factor on wind speed; residual = actual − expected. "
    "Positive bars = overperformers, negative = underperformers."
)

COLOR_OVER = "#1f77b4"
COLOR_UNDER = "#d62728"

df_sorted = df.dropna(subset=["performance_score"]).sort_values(
    "performance_score", ascending=True
).reset_index(drop=True)
colors = [COLOR_OVER if v >= 0 else COLOR_UNDER for v in df_sorted["performance_score"]]

fig_lollipop, ax = plt.subplots(figsize=(9, max(6, 0.35 * len(df_sorted))))
y_pos = np.arange(len(df_sorted))

ax.hlines(y=y_pos, xmin=0, xmax=df_sorted["performance_score"], color=colors, linewidth=2, zorder=2)
ax.scatter(df_sorted["performance_score"], y_pos, color=colors, s=90, zorder=3, edgecolor="white", linewidth=0.8)

for yi, val in zip(y_pos, df_sorted["performance_score"]):
    offset = 0.3 if val >= 0 else -0.3
    ha = "left" if val >= 0 else "right"
    ax.text(val + offset, yi, f"{val:+.1f}", va="center", ha=ha, fontsize=9)

ax.axvline(0, color="black", linewidth=1, zorder=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(df_sorted["country"], fontsize=10)
ax.set_xlabel("Performance residual (percentage points, actual − expected capacity factor)")
ax.set_title("Wind Capacity Factor: Over- vs. Underperformance Relative to Wind Speed", fontsize=13, fontweight="bold", pad=15)

overperform_patch = plt.Line2D([0], [0], marker="o", color=COLOR_OVER, linestyle="-", label="Overperformer")
underperform_patch = plt.Line2D([0], [0], marker="o", color=COLOR_UNDER, linestyle="-", label="Underperformer")
ax.legend(handles=[overperform_patch, underperform_patch], loc="lower right", frameon=False)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.4, zorder=0)
plt.tight_layout()

st.pyplot(fig_lollipop)

st.header("Multi-Metric Country Comparison (Radar Chart)")
st.caption(
    "Each metric is min-max normalized across all countries (0 = lowest, "
    "1 = highest) so wind speed, power density, capacity, generation, and "
    "capacity factor can share one axis scale. Hover shows the real values."
)

RADAR_METRICS = {
    "Mean wind speed": "wind_speed_100m_mean_ms",
    "Mean power density": "power_density_100m_mean_wm2",
    "Installed capacity": "wind_capacity_gw",
    "Generation": "wind_generation_twh",
    "Capacity factor": "capacity_factor_pct",
}

default_countries = (
    df.sort_values("wind_speed_100m_mean_ms", ascending=False)["country"].head(3).tolist()
)

selected_countries = st.multiselect(
    "Countries to compare",
    options=sorted(df["country"].unique()),
    default=default_countries,
    key="radar_country_picker",
)

if selected_countries:
    df_radar = df.copy()
    labels = list(RADAR_METRICS.keys())
    cols = list(RADAR_METRICS.values())

    # Min-max normalize each metric across the full dataset (not just selection)
    norm = df_radar[cols].copy()
    for c in cols:
        lo, hi = df_radar[c].min(), df_radar[c].max()
        norm[c] = (df_radar[c] - lo) / (hi - lo) if hi > lo else 0.5
    df_radar[[f"{c}_norm" for c in cols]] = norm

    fig_radar = go.Figure()
    for country in selected_countries:
        row = df_radar[df_radar["country"] == country].iloc[0]
        r_values = [row[f"{c}_norm"] for c in cols] + [row[f"{cols[0]}_norm"]]
        theta_labels = labels + [labels[0]]
        raw_values = [row[c] for c in cols] + [row[cols[0]]]

        fig_radar.add_trace(
            go.Scatterpolar(
                r=r_values,
                theta=theta_labels,
                fill="toself",
                name=country,
                customdata=raw_values,
                hovertemplate="%{theta}: %{customdata:.2f}<extra>%{fullData.name}</extra>",
            )
        )

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=550,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )

    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.info("Pick at least one country to display the radar chart.")

with st.expander("Show underlying data table"):
    st.dataframe(
        df[
            [
                "country",
                "wind_speed_100m_mean_ms",
                "power_density_100m_mean_wm2",
                "wind_capacity_gw",
                "wind_generation_twh",
                "capacity_factor_pct",
                "performance_score",
            ]
        ]
        .sort_values(color_col, ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )