import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

SOL, ROR, RES = "Solar", "Hydro Run-of-River", "Hydro water reservoir"
TECHS = [SOL, ROR, RES]
COLOR = {SOL: "goldenrod", ROR: "steelblue", RES: "darkslateblue"}


@st.cache_data
def load():
    df = pd.read_csv("data/Q1_Data/panel_daily.csv", index_col=0, parse_dates=True)
    df = df.rename(columns={"Hydro Run-of-River": ROR,
                            "Hydro water reservoir": RES})
    return df[df.index.month.isin([6, 7, 8, 9])]


def heatwaves(df, percentile):
    """Days above the percentile of July/August temperatures, at least 3 in a row."""
    thr = df[df.index.month.isin([7, 8])]["temperature_2m_max"].quantile(percentile)
    hot = df["temperature_2m_max"] >= thr
    return thr, hot & (hot.groupby((hot != hot.shift()).cumsum()).transform("size") >= 3)


df = load()

st.title("Heatwaves, solar and hydro power in Spain")
st.markdown("""
**How does a heatwave affect solar and hydro generation in Spain between 2015
and 2024, and which effect dominates?**

Solar panels lose efficiency as they heat up. Hydro power splits in two:
run-of-river follows the river level, while reservoirs are released on demand —
and demand rises when air conditioners switch on.
""")

# --- Graph 1 (interactive): one summer -------------------------------------
st.subheader("Each summer in detail")

year = st.selectbox("Year", sorted(df.index.year.unique()), index=7)
thr0, hw0 = heatwaves(df, 0.85)
s = df[df.index.year == year]
h = hw0[hw0.index.year == year]

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(s.index, s["temperature_2m_max"], color="firebrick", lw=1)
ax.axhline(thr0, color="firebrick", ls=":", lw=1)
for _, g in s[h].groupby((~h).cumsum()[h]):
    ax.axvspan(g.index[0], g.index[-1], color="orange", alpha=0.3, lw=0)
ax.set_ylabel("Tmax (°C)", color="firebrick")
ax.tick_params(axis="y", labelcolor="firebrick")

ax2 = ax.twinx()
for tech in TECHS:
    ax2.plot(s.index, s[tech] / 1000, color=COLOR[tech], lw=1, label=tech)
ax2.set_ylabel("GWh/day")
ax2.legend(loc="upper left", fontsize=7)
fig.tight_layout()
st.pyplot(fig)
st.caption("Orange areas mark heatwaves. Solar output grows across the years — "
           "that is new capacity being built, not weather.")

# --- Graph 2 (static): average difference on heatwave days -----------------
st.subheader("How much more or less is produced on heatwave days?")

# Only July and August, so heatwave days are compared against days of similar
# day length. Each day is divided by its own year's average, which removes the
# effect of the growing solar fleet.
ja = df[df.index.month.isin([7, 8])]
_, hw_ja = heatwaves(df, 0.85)
hw_ja = hw_ja[hw_ja.index.month.isin([7, 8])]

rel = ja[TECHS] / ja.groupby(ja.index.year)[TECHS].transform("mean")
diff = 100 * (rel[hw_ja].mean() / rel[~hw_ja].mean() - 1)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(TECHS, diff.values, color=[COLOR[t] for t in TECHS], width=0.55)
for i, v in enumerate(diff.values):
    ax.text(i, v + (0.4 if v >= 0 else -0.4), f"{v:+.1f} %",
            ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
ax.axhline(0, color="black", lw=0.8)
ax.set_ylabel("Difference on heatwave days (%)")
ax.set_ylim(min(diff.min() * 1.5, -6), max(diff.max() * 1.5, 6))
fig.tight_layout()
st.pyplot(fig)
st.caption("Average output on heatwave days compared to other July and August "
           "days of the same year. Reservoir hydro is ramped up, while solar and "
           "run-of-river drop slightly.")

# --- Graph 3 (interactive): temperature effect on modules ------------------
st.subheader("Temperature effect on solar modules")

percentile = st.slider("Heatwave threshold (percentile)", 0.80, 0.95, 0.85, 0.01)
thr, hw = heatwaves(df, percentile)
st.caption(f"Threshold {thr:.1f} °C · {int(hw.sum())} heatwave days")

d = df.copy()
d["yield"] = d[SOL] / d["shortwave_radiation_sum"]
d["yield"] /= d.groupby(d.index.year)["yield"].transform("mean")
x, y, m_hw = d["temperature_2m_max"], d["yield"], hw.to_numpy()
slope, intercept = np.polyfit(x, y, 1)

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(x[~m_hw], y[~m_hw], s=8, color="lightsteelblue", edgecolor="none",
           label="normal days")
ax.scatter(x[m_hw], y[m_hw], s=16, color="orangered", edgecolor="none",
           label="heatwave days")
ax.plot([x.min(), x.max()],
        [slope * x.min() + intercept, slope * x.max() + intercept],
        color="black", lw=1.5)
ax.set_xlabel("Tmax (°C)")
ax.set_ylabel("Yield per solar radiation")
ax.set_title(f"{slope * 100:+.2f} % per kelvin", fontsize=10)
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
st.pyplot(fig)
st.caption("Solar output divided by incoming radiation, normalised per year. "
           "What remains is roughly the efficiency loss of the modules. Silicon "
           "photovoltaics lose about 0.4 % per kelvin.")

st.caption("Data (CC BY 4.0): Energy-Charts, Fraunhofer ISE · Open-Meteo (ERA5)")