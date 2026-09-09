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
    st.header("Negative Correlation between Snow Depth and Solar Energy Output")
    st.markdown(
    "Filtered by summer, autumn and winter, snow depth has a strong negative correlation with solar energy utilization across both regions. This can be explained by the solar panels being physically impeded by a layer of snow, and that snow is correlated with less shortwave radiation in general.  "
    "\nThe interesting aspect of this correlation is the steep drop off to zero, which resembles asymptotic decay. One can also see how starting at a certain depth, there's actually an upwards trend again, at different point in both regions; Hovering over the relevant values reveals that these values are concentrated around January and February, where solar activity increases again. This implies that snow might be a secondary driver here, as it directly correlates with a decrease in solar activity.  "
    "\nFiltered by just spring, where solar activity picks up again, one can see a much more gradual decline."
    )
elif st.session_state.preset == "Wind":
    st.header("Linear Growth of Turbine Output in Relation to Wind Speed")
    st.markdown(
    "At the micro-scale, wind speed has a cubic relationship with turbine activity (bounded by automatic shut-offs); wind power is proportional to the cube of the wind speed, therefore one would usually expect an equally non-linear correlation. "
    "\nThis on the other hand showcases a strong positive linear correlation in both regions, which is likely the result of macro-scale regional variation, and smoothing of data."
    )
elif st.session_state.preset == "Hydro":
    st.header("Precipitation and Economic Incentives in the North")
    st.markdown(
    "When taking on this project we had little knowledge on this topic, which is why we intuitively expected there to be a strong positive correlation here; the more precipitation, the more flowing water that generates electricity. Though in this case, its main driver is the economy. When filtered by seasons, you can see a generally strong negative correlation between precipitation and hydro energy generation in the north, the strongest correlation being in winter. The south on the other hand consistently shows a negligible correlation.  "
    "\nThe main correlation we are looking at though is between wind speed and hydro energy utilization in winter. In northern Europe, winter precipitation is often accompanied by strong winds as well, which implies here that the main economic factor lies in the utilization of cheaper wind energy instead of hydro energy, which could be used as a reserve for when electricity is more scarce in the long-run."
    )
elif st.session_state.preset == "Bioenergy":
    st.header("Effect of Apparent Temperature on Bioenergy Utilization")
    st.markdown(
    "This correlation shows a regional divide; in the north, bioenergy utilization is moderately strongly correlated with a decrease in minimum apparent temperature; while the south has a weak, positive correlation. This showcases how bioenergy is utilized in central heating in northern countries, experiencing an uptick in the colder months.  "
    "\nSouthern European countries on the other hand barely rely on centralized district heating, so the positive correlation *could* be explained with a higher overall demand for electricity."
    )

preset_dict = {
    "Spring": ("Spearman", "Solar", "Snow_Depth", ["Spring"]),
    "Wind": ("Pearson", "Wind", "Wind_Speed_100m",["Spring", "Summer", "Autumn", "Winter"]),
    "Wind Speed": ("Spearman", "Hydro", "Wind_Speed_100m",["Winter"]),
    "Bioenergy": ("Spearman", "Bioenergy", "Apparent_Temperature_Min", ["Spring", "Summer", "Autumn", "Winter"]),
    "Rest of the Year": ("Spearman", "Solar", "Snow_Depth", ["Summer", "Autumn", "Winter"]),
    "Precipitation": ("Spearman", "Hydro", "Precipitation_Sum",["Winter"])
}

presets = st.segmented_control("Select a Preset", ["Solar", "Wind", "Hydro", "Bioenergy"], selection_mode="single", default=None, key="preset")


if presets is not None:
    if presets == "Solar":
        options = st.segmented_control("Select a Preset", ["Spring","Rest of the Year"], selection_mode="single", required=True, default= "Spring")
        method, tech, weather, seasons = preset_dict[options]
    elif presets == "Hydro":
        options = st.segmented_control("Select a Preset", ["Wind Speed","Precipitation"], selection_mode="single", required=True, default= "Wind Speed")
        method, tech, weather, seasons = preset_dict[options]
    else:
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
        
        fig.add_trace(go.Scattergl(
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
                
                fig.add_trace(go.Scattergl(
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
                        fig.add_trace(go.Scattergl(
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
