#AI-assisted code
#Debugged with Claude
#Used for text
#Adapted by authors


import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
from scipy import stats

st.set_page_config(page_title="Wind", layout="wide")

COLOR_OVER = "#1f77b4"
COLOR_UNDER = "#d62728"

st.title(" Wind Resource & Performance Analysis")

st.markdown(
    """
Question: Do countries with **higher average wind speeds** generate **proportionally more electricity**
per installed turbine capacity than countries with lower wind speeds, and which countries
over- or underperform relative to their raw wind potential?
"""
)

df = pd.read_csv("./data/Q5_Data/wind.csv")

st.subheader("Key metrics")

st.markdown("**Capacity factor**: how efficiently installed capacity is used?")
st.latex(r"""
\text{Capacity factor (\%)} = \frac{\text{Actual generation (TWh)}}
{\text{Installed capacity (GW)} \times 8760\ \text{h}} \times 100
""")
st.markdown(
    "8,760 is the number of hours in a year, so the denominator is the "
    "theoretical maximum a country's turbines could generate if they ran at "
    "full capacity every hour of the year. A higher capacity factor means "
    "the installed turbines are producing closer to their theoretical maximum."
)

st.markdown("**Performance score**: does a country do better or worse than its wind speed alone predicts?")
st.markdown(
    "Performance score = actual capacity factor minus the value expected from mean wind speed alone."
)

col_formula1, col_formula2 = st.columns(2)
with col_formula1:
    st.latex(r"\text{Expected CF} = \text{intercept} + \text{slope} \times \text{wind speed}")
with col_formula2:
    st.latex(r"\text{Performance score} = \text{Actual CF} - \text{Expected CF}")

st.markdown(
    "- 🔵 **Positive score** → overperformer: more electricity per installed capacity than its wind speed would suggest "
    "(e.g. good turbine siting, newer technology, strong grid integration).\n"
    "- 🔴 **Negative score** → underperformer: less electricity than expected "
    "(e.g. older turbine fleet, grid curtailment, regulatory constraints)."
)

"""
Example Performance score
"""
reg_data = df.dropna(subset=["wind_speed_100m_mean_ms", "capacity_factor_pct"])

slope, intercept, r_value, p_value, std_err = stats.linregress(
    reg_data["wind_speed_100m_mean_ms"],
    reg_data["capacity_factor_pct"],
)

df["expected_capacity_factor"] = intercept + slope * df["wind_speed_100m_mean_ms"]
df["performance_score"] = df["capacity_factor_pct"] - df["expected_capacity_factor"]

top_over = df.loc[df["performance_score"].idxmax()]
top_under = df.loc[df["performance_score"].idxmin()]

st.markdown(
    f"""
**example:**
"""
)
st.latex(r"\text{Expected CF} = \text{intercept} + \text{slope} \times \text{wind speed}")
st.markdown(
    f"""
The intercept ({intercept:.1f}) and slope ({slope:.2f}) come directly from fitting the
regression line through all {len(reg_data)} countries. 

**{top_over['country']}** has a mean wind speed of {top_over['wind_speed_100m_mean_ms']:.1f} m/s,
so its expected capacity factor is {intercept:.1f} + {slope:.2f} × {top_over['wind_speed_100m_mean_ms']:.1f}
= **{top_over['expected_capacity_factor']:.1f}%**. Its actual capacity factor is
{top_over['capacity_factor_pct']:.1f}%, so its performance score is
**{top_over['performance_score']:+.1f} pp**.

**{top_under['country']}**, by contrast, has a mean wind speed of
{top_under['wind_speed_100m_mean_ms']:.1f} m/s, giving an expected capacity factor of
{intercept:.1f} + {slope:.2f} × {top_under['wind_speed_100m_mean_ms']:.1f}
= **{top_under['expected_capacity_factor']:.1f}%**. But its actual capacity factor is only
{top_under['capacity_factor_pct']:.1f}%. A performance score of
**{top_under['performance_score']:+.1f} pp**.
"""
)

# exeample
top_over = df.loc[df["country"] == "Italy"].iloc[0]
top_under = df.loc[df["country"] == "Argentina"].iloc[0]

st.markdown(
    """
**example:**
"""
)

fig_example, ax_example = plt.subplots(figsize=(5.5, 4))

x_line = np.linspace(reg_data["wind_speed_100m_mean_ms"].min() - 0.5,
                      reg_data["wind_speed_100m_mean_ms"].max() + 0.5, 100)
y_line = intercept + slope * x_line
ax_example.plot(x_line, y_line, color="black", linewidth=1.5, label="Regression line (expected CF)")

ax_example.scatter([top_over["wind_speed_100m_mean_ms"]], [top_over["capacity_factor_pct"]],
                    color=COLOR_OVER, zorder=3, s=80)
ax_example.plot([top_over["wind_speed_100m_mean_ms"]] * 2,
                [top_over["expected_capacity_factor"], top_over["capacity_factor_pct"]],
                color=COLOR_OVER, linestyle="--", linewidth=1.2)
ax_example.annotate(f"{top_over['country']}\n({top_over['performance_score']:+.1f} pp)",
                     (top_over["wind_speed_100m_mean_ms"], top_over["capacity_factor_pct"]),
                     textcoords="offset points", xytext=(8, 4), fontsize=8, color=COLOR_OVER)

ax_example.scatter([top_under["wind_speed_100m_mean_ms"]], [top_under["capacity_factor_pct"]],
                    color=COLOR_UNDER, zorder=3, s=80)
ax_example.plot([top_under["wind_speed_100m_mean_ms"]] * 2,
                [top_under["expected_capacity_factor"], top_under["capacity_factor_pct"]],
                color=COLOR_UNDER, linestyle="--", linewidth=1.2)
ax_example.annotate(f"{top_under['country']}\n({top_under['performance_score']:+.1f} pp)",
                     (top_under["wind_speed_100m_mean_ms"], top_under["capacity_factor_pct"]),
                     textcoords="offset points", xytext=(8, -18), fontsize=8, color=COLOR_UNDER)

ax_example.set_xlabel("Mean wind speed (m/s)", fontsize=9)
ax_example.set_ylabel("Capacity factor (%)", fontsize=9)
ax_example.set_title("Performance score", fontsize=10, fontweight="bold")
ax_example.tick_params(labelsize=8)
ax_example.spines[["top", "right"]].set_visible(False)
ax_example.grid(alpha=0.3)
plt.tight_layout()

st.pyplot(fig_example)


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
st.header("Global Wind Resource & Performance Map")
st.markdown(
    "We start with a world map because the question is inherently spatial: "
    "is there a geographic pattern to which countries turn wind into "
    "electricity efficiently, and which don't? The map below lets you "
    "switch between two views. **Capacity factor** shows the raw "
    "efficiency number for every country. Useful for spotting the overall "
    "leaders and laggards at a glance. **Performance score** instead shows "
    "the regression residual explained above, which is the more interesting "
    "view for our actual question: it strips out the part of the "
    "difference that wind speed alone explains, so what's left on the map "
    "is specifically the over and underperformance relative to each "
    "country's own wind potential. Hover over any country to see its exact "
    "wind speed, power density, installed capacity, and generation."
)

# Map: capacity factor or performance score
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

fig.update_geos(
    showcountries=True,
    countrycolor="lightgray",
    showcoastlines=False,
    lataxis_showgrid=True,
    lataxis_gridcolor="lightgray",
    lonaxis_showgrid=True,
    lonaxis_gridcolor="lightgray",
)
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


# lollipop chart: over vs. underperformers
st.header("Ranked Performance Residuals")
st.markdown(
    "The map shows performance scores geographically, but it makes it hard "
    "to directly compare specific countries against each other or read off "
    "exact values. This chart isolates the actual answer to the second part "
    "of our research question, which countries over or underperform, by "
    "ranking countries on their performance score alone. Bars pointing "
    "right (blue) are countries generating more electricity from their "
    "installed capacity than their wind speed would predict, bars pointing "
    "left (red) are generating less. By default we show the 3 strongest "
    "over- and underperformers so the chart stays readable, but you can use "
    "the dropdowns below to swap in any other country and compare it "
    "directly against these reference cases."
)


df_perf = df.dropna(subset=["performance_score"])

overperformers_sorted = df_perf[df_perf["performance_score"] > 0].sort_values(
    "performance_score", ascending=False
)
underperformers_sorted = df_perf[df_perf["performance_score"] < 0].sort_values(
    "performance_score", ascending=True
)

col_over, col_under = st.columns(2)
with col_over:
    selected_over = st.multiselect(
        "Overperforming countries",
        options=overperformers_sorted["country"].tolist(),
        default=overperformers_sorted["country"].head(3).tolist(),
        key="lollipop_overperformers",
    )
with col_under:
    selected_under = st.multiselect(
        "Underperforming countries",
        options=underperformers_sorted["country"].tolist(),
        default=underperformers_sorted["country"].head(3).tolist(),
        key="lollipop_underperformers",
    )

selected_countries = selected_over + selected_under

if selected_countries:
    df_sorted = df_perf[df_perf["country"].isin(selected_countries)].sort_values(
        "performance_score", ascending=True
    ).reset_index(drop=True)
    colors = [COLOR_OVER if v >= 0 else COLOR_UNDER for v in df_sorted["performance_score"]]

    fig_lollipop, ax = plt.subplots(figsize=(9, max(4, 0.5 * len(df_sorted))))
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
    ax.grid(axis="both", linestyle="--", alpha=0.4, zorder=0)
    plt.tight_layout()

    st.pyplot(fig_lollipop)
else:
    st.info("Select at least one country in either dropdown to display the chart.")


# Interactive radar chart: multi-metric country comparison
st.header("Multi-Metric Country Comparison")
st.markdown(
    "The map and the ranked chart both focus on a single number, capacity "
    "factor or performance score, but they can't show *why* a country ends "
    "up over or underperforming. This radar chart lets you compare several "
    "countries across all five underlying metrics at once: wind speed, "
    "power density, installed capacity, generation, and capacity factor. "
    "This makes it possible to see, for example, whether a country's high "
    "performance score comes from a genuinely strong wind resource, from a "
    "comparatively small but well-utilized turbine fleet, or from some "
    "other combination of factors. Since the five metrics have completely "
    "different units and scales, each one is normalized to a 0-1 range "
    "before plotting (explained further below) so they can share one axis "
    "without one metric visually dominating the others."
)
st.caption(
    "Each metric is min-max normalized across all countries (0 = lowest, "
    "1 = highest) so wind speed (m/s), power density (W/m²), installed "
    "capacity (GW), generation (TWh), and capacity factor (%) can share one "
    "axis scale. Hover over a point to see the real, non-normalized value."
)

RADAR_METRICS = {
    "Mean wind speed (m/s)": "wind_speed_100m_mean_ms",
    "Mean power density (W/m²)": "power_density_100m_mean_wm2",
    "Installed capacity (GW)": "wind_capacity_gw",
    "Generation (TWh)": "wind_generation_twh",
    "Capacity factor (%)": "capacity_factor_pct",
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
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], showgrid=True, gridcolor="lightgray"),
            angularaxis=dict(showgrid=True, gridcolor="lightgray"),
        ),
        height=550,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )

    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.info("Pick at least one country to display the radar chart.")


# Supporting table (sorted by chosen metric)
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