import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

SOL, ROR, RES = "Solar", "Hydro Running", "Hydro Reservoir"
TECHS = [SOL, ROR, RES]
NAME = {SOL: "Solar", ROR: "Hydro Running", RES: "Hydro Reservoir"}
COLOR = {SOL: "goldenrod", ROR: "steelblue", RES: "darkslateblue"}

@st.cache_data
def load():
    df = pd.read_csv("data/Q1_Data/panel_daily.csv", index_col=0, parse_dates=True)
    return df[df.index.month.isin([6, 7, 8, 9])]


@st.cache_data
def effect(percentile):
    df = load()
    thr = df[df.index.month.isin([7, 8])]["temperature_2m_max"].quantile(percentile)
    hot = df["temperature_2m_max"] >= thr
    hw = hot & (hot.groupby((hot != hot.shift()).cumsum()).transform("size") >= 3)
    near = hw.rolling(7, center=True, min_periods=1).max().astype(bool).to_numpy()

    idx, rows = df.index, []
    for pos in np.flatnonzero(hw.to_numpy()):
        t = idx[pos]
        cand = ~near & (idx.year == t.year) & (np.abs((idx - t).days) <= 15)
        if cand.sum() >= 3:
            rows.append({"year": t.year, **{
                c: df[c].iloc[pos] - df[c].to_numpy()[cand].mean() for c in TECHS}})
    return thr, hw, pd.DataFrame(rows)




st.title("How does a heatwave event simultaneously affect solar generation output and hydro generation output in Spain between 2015 and 2024, and which effect dominates in net MWh terms?")

df = load()


st.subheader("Each summer in detail")

year = st.selectbox("year", sorted(df.index.year.unique()), index=7)
thr0, hw0, _ = effect(0.85)
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
    ax2.plot(s.index, s[tech] / 1000, color=COLOR[tech], lw=1, label=NAME[tech])
ax2.set_ylabel("GWh/day")
ax2.legend(loc="upper left", fontsize=7)
fig.tight_layout()
st.pyplot(fig)
st.caption("Orange areas mark heatwaves. Solar capacity rises overall each year, which is caused by new installation and not the weather")




st.subheader("Which effect is bigger?")

percentile = st.slider("Heat wave threshold)",
                      0.80, 0.95, 0.85, 0.01)
thr, hw, eff = effect(percentile)
st.caption(f"threshold {thr:.1f} °C · {int(hw.sum())} Heat wave days · "
           f"{len(eff)} evaluated from this")
c = st.columns(3)
for i, tech in enumerate(TECHS):
    c[i].metric(NAME[tech], f"{eff[tech].mean():+,.0f} MWh/Day")
per_year = eff.groupby("year")[TECHS].sum() / 1000
fig, ax = plt.subplots(figsize=(8, 3.5))
pos = np.zeros(len(per_year))
neg = np.zeros(len(per_year))
for tech in TECHS:
    v = per_year[tech].to_numpy()
    ax.bar(per_year.index, v, bottom=np.where(v >= 0, pos, neg),
           color=COLOR[tech], label=NAME[tech])
    pos = np.where(v >= 0, pos + v, pos)
    neg = np.where(v < 0, neg + v, neg)
ax.plot(per_year.index, per_year.sum(axis=1), color="black", marker="o",
        lw=1.4, ms=4, label="Net")
ax.axhline(0, color="black", lw=0.8)
ax.set_xlabel("year")
ax.set_ylabel("Effect (GWh)")
ax.legend(fontsize=7)
fig.tight_layout()
st.pyplot(fig)
st.caption("Sum of all heatwave days in a year.")




st.subheader("Temperature effect on solar modules")

d = df.copy()
d["yield"] = d[SOL] / d["shortwave_radiation_sum"]
d["yield"] /= d.groupby(d.index.year)["yield"].transform("mean")
x, y = d["temperature_2m_max"], d["yield"]
m, b = np.polyfit(x, y, 1)

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(x, y, s=8, color="lightsteelblue", edgecolor="none")
ax.plot([x.min(), x.max()], [m * x.min() + b, m * x.max() + b],
        color="black", lw=1.5)
ax.set_xlabel("Tmax (°C)")
ax.set_ylabel("Yield per solar radiation")
ax.set_title(f"{m * 100:+.2f} % per kelvin", fontsize=10)
fig.tight_layout()
st.pyplot(fig)
