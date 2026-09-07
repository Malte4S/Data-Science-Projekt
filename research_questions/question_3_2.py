# AI assisted code used for graphing and plots.
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
import statsmodels.api as sm
from datetime import date


if "preset" not in st.session_state:
    st.session_state.preset = None

if st.session_state.preset is None:
    st.header("Analysis of Four Correlations")
    st.markdown(
    "From the previous sandbox of visualizations, we have identified multiple significant correlations between weather variables and renewable energy generation. Of each energy technology, we've decided to highlight one particularly interesting correlation for further analysis.  "
    "\n**Select one of the four presets below to view our chosen correlation for each technology.**"
    )
elif st.session_state.preset == "Solar":
    st.header("Solar Correlation")
    st.markdown(
    "test description: Snow depth has strong negative correlation due to a)it covering the panels, and b) it being associated with cold weather and low solar activity. The interesting thing is that this correlation only shines through if you separate spring from the rest of the year. in the spring the drop off is much more gradual, here it's very cliffy so to speak. On top of that, the activity actually goes up with higher snow depth, likely because higher snow depth is correlated with sunnier and clearer weather."
    )
elif st.session_state.preset == "Wind":
    st.header("Wind Correlation")
    st.markdown(
    "test description: at the micro level, the relation is cubic; wind speed cubed it wind power, therefore wind speed and generation should be cubed as well. but this shows, that at the macro level, it averages itself out into a linear relationship, whether this is due to turbine clamping, or just weather variation"
    )
elif st.session_state.preset == "Hydro":
    st.header("Hydro Correlation")
    st.markdown(
    "test description: why wind? well, you'd firstly just intuitively expect precipitation to meaning more hydro, but here's where economics come into play; hydro is a giant physical batter, so the logic is that when it rains, you better store the water rather than let it run, which is why the baseline correlation is reasonably negative in the north. the south on the other hand doesnt seem to engage in this electricity hoarding business like reasonable ppl humph! anyway, in the winter it's particularly pronounced, since heavy storms bring heavy precipitation, and what do storm bring as well? wind! and where there is an overflow of cheap wind energy, theres even less incentive to use hydro; better to hoard it and sell when prices are high"
    )
elif st.session_state.preset == "Bioenergy":
    st.header("Bioenergy Correlation")
    st.markdown(
    "test description: this is interesting in that the south and the north show opposite correlations; the north appears to be utilizing bio much more when its getting colder (apparent temp is felt temp), so they dispatch for heating. the south on the other hand has a rather weak positive correlation, which could imply they use it as it's getting warmer, maybe because the stuff they use to burn gets cheaper in the summer, or becauses of ACs (yuck ACs, never heard of Stroßlüften??)"
    )

preset_dict = {
    "Solar": ("Spearman", "Solar", "Snow_Depth", ["Summer", "Autumn", "Winter"]),
    "Wind": ("Pearson", "Wind", "Wind_Speed_100m",["Spring", "Summer", "Autumn", "Winter"]),
    "Hydro": ("Spearman", "Hydro", "Wind_Speed_100m",["Winter"]),
    "Bioenergy": ("Spearman", "Bioenergy", "Apparent_Temperature_Min", ["Spring", "Summer", "Autumn", "Winter"])
}

presets = st.segmented_control("Select a Preset", ["Solar", "Wind", "Hydro", "Bioenergy"], selection_mode="single", default=None, key="preset")

if presets is not None:
    method, tech, weather, seasons = preset_dict[presets]

    GEN_FILE = "./data/Q3_Data/European_Daily_Generation_2023_2025.csv"
    CAP_FILE = "./data/Q3_Data/European_Validated_Capacity_2023_2025.csv"
    WEATHER_FILE = "./data/Q3_Data/Regional_Weighted_Weather_2023_2025.csv"

    if "zoom" not in st.session_state:
        st.session_state.zoom = 600

    def calculate_spearman_ci(rho, n):
        if abs(rho) == 1.0:
            return rho, rho
        z = np.arctanh(rho)
        se = 1 / np.sqrt(n - 3)
        z_crit = stats.norm.ppf(0.975)
        ci_low = np.tanh(z - z_crit * se)
        ci_high = np.tanh(z + z_crit * se)
        return ci_low, ci_high

    # 1. Targeted File Loading
    gen_cols = ['Region', 'Country', 'Date', tech]
    cap_cols = ['Region', 'Country', 'Year', tech]
    weather_cols = ['Region', 'Date', weather]

    gen_df = pd.read_csv(GEN_FILE, usecols=gen_cols).rename(columns={tech: 'Daily_MWh'})
    cap_df = pd.read_csv(CAP_FILE, usecols=cap_cols).rename(columns={tech: 'Capacity_MW'})
    weather_df = pd.read_csv(WEATHER_FILE, usecols=weather_cols)

    gen_df['Year'] = gen_df['Date'].str[:4].astype(int)

    # 2. Direct Merge
    merged = pd.merge(gen_df, cap_df, on=['Region', 'Country', 'Year'], how='inner')
    merged = merged.dropna(subset=['Daily_MWh'])
    merged['Daily_Potential_MWh'] = merged['Capacity_MW'] * 24

    # 3. Dynamic Date Slicing & Single Aggregation
    slice_len = 10
    merged['Period'] = merged['Date'].str[:slice_len]
    weather_df['Period'] = weather_df['Date'].str[:slice_len]

    final_gen = merged.groupby(['Region', 'Period']).agg({'Daily_MWh': 'sum', 'Daily_Potential_MWh': 'sum'}).reset_index()
    final_gen['CF'] = final_gen['Daily_MWh'] / final_gen['Daily_Potential_MWh']

    final_weather = weather_df.groupby(['Region', 'Period'])[[weather]].mean().reset_index()
    final_df = pd.merge(final_gen, final_weather, on=['Region', 'Period'])

    # --- INSERT SEASONAL LOGIC HERE ---
    # 1. Extract the numerical month (characters 5 and 6) from 'YYYY-MM' or 'YYYY-MM-DD'
    final_df['Month_Num'] = final_df['Period'].str[5:7].astype(int)

    # 2. Map the month integers to standard meteorological seasons
    def map_season(m):
        if m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        elif m in [9, 10, 11]: return 'Autumn'
        else: return 'Winter'
        
    final_df['Season'] = final_df['Month_Num'].apply(map_season)

    # 3. Filter the dataframe if the user has clicked any buttons
    if seasons:
        final_df = final_df[final_df['Season'].isin(seasons)]
    # --- END SEASONAL LOGIC ---

    # 4. Visualization Setup
    colors = {'Northern Europe': '#1f77b4', 'Southern Europe': '#ff7f0e'}
    clean_var_name = weather.replace('_', ' ').title()

    # Extract loop invariants
    dot_size = 5 
    dot_alpha = 0.5 
    line_width = 0 

    fig = go.Figure()

    # 5. Native Groupby Looping
    for r, r_data in final_df.groupby('Region'):
        r_data = r_data.dropna(subset=[weather, 'CF'])
        x = r_data[weather].values
        y = r_data['CF'].values
        periods = r_data['Period'].values
        n_samples = len(x)
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='markers',
            marker=dict(
                color=colors.get(r, 'gray'),
                size=dot_size,
                opacity=dot_alpha,
                line=dict(width=line_width, color='black')
            ),
            name=f"{r} Data",
            text=periods,
            hovertemplate=(
                f"<b>{r}</b><br>"
                "Date/Period: %{text}<br>"
                f"{clean_var_name}: %{{x:.2f}}<br>"
                "Capacity Factor: %{y:.4f}<extra></extra>"
            ),
            showlegend=False
        ))
        
        if method == "Pearson":
            if n_samples >= 3:
                slope, intercept, _, _, _ = stats.linregress(x, y)
                x_line = np.array([x.min(), x.max()])
                y_line = slope * x_line + intercept
                
                res_p = stats.pearsonr(x, y)
                ci_p = res_p.confidence_interval(confidence_level=0.95)
                p_val_str = "<0.001" if res_p.pvalue < 0.001 else f"{res_p.pvalue:.3f}"
                
                label_text = (f"<b>{r} (N={n_samples})</b><br>"
                                f"r = {res_p.statistic:.2f} (p {p_val_str})<br>"
                                f"95% CI: [{ci_p.low:.2f}, {ci_p.high:.2f}]")
                
                fig.add_trace(go.Scatter(
                    x=x_line, y=y_line,
                    mode='lines',
                    line=dict(color=colors.get(r, 'gray'), dash='dash', width=3),
                    name=label_text,
                    hoverinfo='skip'
                ))
        elif method == "Spearman":
                    if n_samples >= 4:
                        res_s = stats.spearmanr(x, y)
                        rho = res_s.statistic
                        ci_low, ci_high = calculate_spearman_ci(rho, n_samples)
                        p_val_str = "<0.001" if res_s.pvalue < 0.001 else f"{res_s.pvalue:.3f}"
                        
                        label_text = (f"<b>{r} (N={n_samples})</b><br>"
                                        f"ρ = {rho:.2f} (p {p_val_str})<br>"
                                        f"95% CI: [{ci_low:.2f}, {ci_high:.2f}]")
                        
                        # 1. Sort the data sequentially so the smoothing line draws cleanly left-to-right
                        sorted_indices = np.argsort(x)
                        x_sorted = x[sorted_indices]
                        y_sorted = y[sorted_indices]
        
                        # 2. Calculate the LOWESS curve (frac=0.3 means it evaluates 30% of the data at a time for smoothness)
                        lowess = sm.nonparametric.lowess(y_sorted, x_sorted, frac=0.3)
                        x_lowess = lowess[:, 0]
                        y_lowess = lowess[:, 1]
        
                        # 3. Draw the curving LOWESS trendline
                        fig.add_trace(go.Scatter(
                            x=x_lowess, y=y_lowess,
                            mode='lines',
                            line=dict(color=colors.get(r, 'gray'), width=3),
                            name=label_text,
                            hoverinfo='skip'
                        ))

    # Graph Formatting
    seasons_str = str(seasons).replace("'", "").replace("[", "").replace("]", "")
    fig.update_layout(
        height=st.session_state.zoom,
        title=dict(
            text=f"<b>{method} Correlation: Daily Capacity Factor vs. {clean_var_name} ({tech}) ({seasons_str})</b>",
            font=dict(size=20)
        ),
        xaxis_title=dict(text=f"Average {clean_var_name}", font=dict(size=14)),
        yaxis_title=dict(text="Capacity Factor (CF)", font=dict(size=14)),
        template="plotly_white",
        hovermode="closest",
        legend=dict(
            title=dict(text=f"<b>Region & {method} Stats</b>"),
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=60, b=0)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    st.plotly_chart(fig, use_container_width=True)


    _, middle, _  = st.columns([0.02, 0.4, 0.5], gap="small")

    with middle:
        st.slider(label="Adjust Plot Height", min_value=600, max_value=1200, value=600,step=10,format="%d", key="zoom")
