#AI-assisted code
#Debugged with Claude

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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


def heatwaves(df, percentile): #days above a heat percentile in july/august (at least 3 days in row!)
    thr = df[df.index.month.isin([7, 8])]["temperature_2m_max"].quantile(percentile)
    hot = df["temperature_2m_max"] >= thr
    return thr, hot & (hot.groupby((hot != hot.shift()).cumsum()).transform("size") >= 3)


df = load()

st.title("Research Question 1")
st.markdown("""
**How does a heatwave affect solar and hydro generation in Spain between 2015
and 2024?**

Solar panels are less efficient under extreme heat. Hydro power splits in two:
Run of River is dependant on the natural water level, while reservoirs are released on demand. 
This demand increases during heatwaves with higher AC usage.
""")

st.subheader("Each summer in detail") #graph 1 interactive

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
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax2 = ax.twinx()

for tech in TECHS:
    ax2.plot(s.index, s[tech] / 1000, color=COLOR[tech], lw=1, label=tech)
ax2.set_ylabel("GWh/day")
ax2.legend(loc="upper left", fontsize=7)
fig.tight_layout()
st.pyplot(fig)
st.caption("Orange areas mark heatwaves. Solar output increases in total over the years which is due to increased capacity and not weather.")


st.subheader("How much more or less is produced on heatwave days?") #graph 2 static

ja = df[df.index.month.isin([7, 8])]
_, hw_ja = heatwaves(df, 0.85)
hw_ja = hw_ja[hw_ja.index.month.isin([7, 8])]

rel = ja[TECHS] / ja.groupby(ja.index.year)[TECHS].transform("mean")
diff = 100 * (rel[hw_ja].mean() / rel[~hw_ja].mean() - 1)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(TECHS, diff.values, color=[COLOR[t] for t in TECHS], width=0.55)

for i, v in enumerate(diff.values):
    ax.text(i, v + (0.4 if v >= 0 else -0.4), f"{v:+.1f} %",ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
ax.axhline(0, color="black", lw=0.8)
ax.set_ylabel("Difference on heatwave days (%)")
ax.set_ylim(min(diff.min() * 1.5, -6), max(diff.max() * 1.5, 6))
fig.tight_layout()
st.pyplot(fig)
st.caption("Average output on heatwave days compared to other July/August days of the same year. "
           "Each day gets divided by its own year average to remove the effect of the increased capacity over time.")


st.subheader("Temperature effect on solar modules") #graph 3 interactive

years = sorted(df.index.year.unique())
first, last = st.slider("Period", min(years), max(years),(min(years), max(years)))
d = df.copy()
d["yield"] = d[SOL] / d["shortwave_radiation_sum"]
d["yield"] /= d.groupby(d.index.year)["yield"].transform("mean")
_, hw = heatwaves(df, 0.85)
keep = (d.index.year >= first) & (d.index.year <= last)
d, m_hw = d[keep], hw.to_numpy()[keep]

x, y = d["temperature_2m_max"], d["yield"]
slope, intercept = np.polyfit(x, y, 1)
st.caption(f"{first}–{last} · {len(d)} days · {int(m_hw.sum())} of them heatwave days")
fig, ax = plt.subplots(figsize=(8, 4))

ax.scatter(x[~m_hw], y[~m_hw], s=8, color="lightsteelblue", edgecolor="none",label="normal days")
ax.scatter(x[m_hw], y[m_hw], s=16, color="orangered", edgecolor="none",label="heatwave days")
ax.plot([x.min(), x.max()],[slope * x.min() + intercept, slope * x.max() + intercept],color="black", lw=1.5)
ax.set_xlabel("Tmax (°C)")
ax.set_ylabel("Yield per solar radiation")
ax.legend(fontsize=8, loc="upper right")

fig.tight_layout()
st.pyplot(fig)
st.caption("Solar output divided by radiation, normalised per year. ")

