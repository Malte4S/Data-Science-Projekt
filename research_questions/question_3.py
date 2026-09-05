import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go

st.set_page_config(
    page_title="Research Question 3",
    layout="wide"
)

st.title("Research Question 3")
st.write("How is renewable electricity generation associated with regional meteorological conditions between Northern and Southern European countries?​")

st.subheader("Context")
st.markdown(
    "This research question concerns itself with the relationship between renewable electricity generation and regional meteorological condition in Northern and Southern European Countries, which were aggregated into said regions based on their geographical location. The analysis was conducted using a Pearson correlation coefficient. "
    "Another approach with the Spearman correlation coefficient was also conducted for comparison, to uncover potential nonlinear relationships, though that did not yield any significant differences in results, which is why the Pearson correlation coefficient was chosen as the primary method of analysis.")

st.subheader("Interactive Visualizations")
st.markdown(
    "Each dot represents, depending on which was selected, a day or month in the 2023-2025 period, with the x-axis representing the meteorological condition and the y-axis representing the renewable electricity generation. The dashed line represents the linear regression line. **Hover over the points to see the specific period and exact values.**")

tech = st.segmented_control("Technology", ['Solar', 'Wind', 'Hydro', 'Bioenergy'], default='Solar')
weather = st.segmented_control("Weather Variable", ['Shortwave_Radiation_Sum', 'Wind_Speed_100m', 'Wind_Speed_100m_Cubed', 'Wind_Gusts_10m_Max', 'Temperature_2m_Max', 'Apparent_Temperature_Min', 'Precipitation_Sum', 'Snow_Depth'], default='Shortwave_Radiation_Sum')
timeframe = st.segmented_control("timeframe", ["Daily", "Monthly"], default="Monthly")

GEN_FILE = "./data/Q3_Data/European_Daily_Generation_2023_2025.csv"
CAP_FILE = "./data/Q3_Data/European_Validated_Capacity_2023_2025.csv"
WEATHER_FILE = "./data/Q3_Data/Regional_Weighted_Weather_2023_2025.csv"

# AI assisted code from here on.
if all([tech, weather, timeframe]):
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
    slice_len = 7 if timeframe == 'Monthly' else 10
    merged['Period'] = merged['Date'].str[:slice_len]
    weather_df['Period'] = weather_df['Date'].str[:slice_len]

    final_gen = merged.groupby(['Region', 'Period']).agg({'Daily_MWh': 'sum', 'Daily_Potential_MWh': 'sum'}).reset_index()
    final_gen['CF'] = final_gen['Daily_MWh'] / final_gen['Daily_Potential_MWh']

    final_weather = weather_df.groupby(['Region', 'Period'])[[weather]].mean().reset_index()
    final_df = pd.merge(final_gen, final_weather, on=['Region', 'Period'])

    # 4. Visualization Setup
    colors = {'Northern Europe': '#1f77b4', 'Southern Europe': '#ff7f0e'}
    clean_var_name = weather.replace('_', ' ').title()
    
    # Extract loop invariants
    dot_size = 5 if timeframe == 'Daily' else 10
    dot_alpha = 0.5 if timeframe == 'Daily' else 0.8
    line_width = 0 if timeframe == 'Daily' else 1
    
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

    # Graph Formatting
    fig.update_layout(
        height=700,
        title=dict(
            text=f"<b>Pearson Correlation: {timeframe} Capacity Factor vs. {clean_var_name} ({tech})</b>",
            font=dict(size=20)
        ),
        xaxis_title=dict(text=f"Average {clean_var_name}", font=dict(size=14)),
        yaxis_title=dict(text="Capacity Factor (CF)", font=dict(size=14)),
        template="plotly_white",
        hovermode="closest",
        legend=dict(
            title=dict(text="<b>Region & Pearson Stats</b>"),
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please select a Technology, Weather Variable, and Timeframe to display the analysis.")
