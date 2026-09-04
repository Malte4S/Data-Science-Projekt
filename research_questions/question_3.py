import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Research Question 3",
    layout="wide"
)

st.title("Research Question 3")
st.write("How is renewable electricity generation associated with regional meteorological conditions between Northern and Southern European countries?​")

st.subheader("Context")
st.markdown(
    "This research question concerns itself with the relationship between renewable electricity generation and regional meteorological condition in Northern and Southern European Countries, which were aggregated into said regions based on their geographical location. The analysis was conducted using a Pearson correlation coefficient. "
    "Another approach with the Spearman correlation coefficient was also conducted for comparison, to uncover potential nonlinear relationships, though that did not yield any significant differences in results, which is why the Pearson correlation coefficient was chosen as the primary method of analysis."
)

st.subheader("Interactive Visualizations")
st.markdown(
    "Each dot represents, depending on which was selected, a day or month in the 2023-2025 period, with the x-axis representing the meteorological condition and the y-axis representing the renewable electricity generation. The dashed line represents the linear regression line."
)

tech = st.segmented_control("Technology", ['Solar', 'Wind', 'Hydro', 'Bioenergy'], default='Solar')
weather = st.segmented_control("Weather Variable", ['Shortwave_Radiation_Sum', 'Wind_Speed_100m', 'Wind_Speed_100m_Cubed', 'Wind_Gusts_10m_Max', 'Temperature_2m_Max', 'Apparent_Temperature_Min', 'Precipitation_Sum', 'Snow_Depth'], default='Temperature_2m_Max')
timeframe = st.segmented_control("Timeframe", ["Daily", "Monthly"], default="Monthly")


# AI-assisted code from here on, used to visualize the Pearson correlation coefficient.
TARGET_TECH = tech
TARGET_WEATHER = weather
TIMEFRAME = timeframe

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
GEN_FILE = "./data/Q3_Data/European_Daily_Generation_2023_2025.csv"
CAP_FILE = "./data/Q3_Data/European_Validated_Capacity_2023_2025.csv"
WEATHER_FILE = "./data/Q3_Data/Regional_Weighted_Weather_2023_2025.csv"

def execute_fast_pipeline():
    # 1. Targeted File Loading (Ignore unnecessary columns on read)
    gen_cols = ['Region', 'Country', 'Date', TARGET_TECH]
    cap_cols = ['Region', 'Country', 'Year', TARGET_TECH]
    weather_cols = ['Region', 'Date', TARGET_WEATHER]

    try:
        gen_df = pd.read_csv(GEN_FILE, usecols=gen_cols).rename(columns={TARGET_TECH: 'Daily_MWh'})
        cap_df = pd.read_csv(CAP_FILE, usecols=cap_cols).rename(columns={TARGET_TECH: 'Capacity_MW'})
        weather_df = pd.read_csv(WEATHER_FILE, usecols=weather_cols)
    except ValueError as e:
        print(f"[!] Initialization Error. Check variable spelling: {e}")
        return

    # 2. Lightning-Fast String Slicing (Bypasses slow datetime parsing)
    gen_df['Year'] = gen_df['Date'].str[:4].astype(int)

    # 3. Direct Merge (Bypasses Melting)
    merged = pd.merge(gen_df, cap_df, on=['Region', 'Country', 'Year'], how='inner')
    merged = merged.dropna(subset=['Daily_MWh'])
    merged['Daily_Potential_MWh'] = merged['Capacity_MW'] * 24

    # 4. Regional Aggregation Base
    agg_gen = merged.groupby(['Region', 'Date']).agg({
        'Daily_MWh': 'sum',
        'Daily_Potential_MWh': 'sum'
    }).reset_index()

    # 5. Timeframe Routing (String slicing for Month aggregation)
    if TIMEFRAME == 'Monthly':
        agg_gen['Period'] = agg_gen['Date'].str[:7]
        weather_df['Period'] = weather_df['Date'].str[:7]
    elif TIMEFRAME == 'Daily':
        agg_gen['Period'] = agg_gen['Date']
        weather_df['Period'] = weather_df['Date']


    # 6. Final Mathematical Aggregation
    final_gen = agg_gen.groupby(['Region', 'Period']).agg({'Daily_MWh': 'sum', 'Daily_Potential_MWh': 'sum'}).reset_index()
    final_gen['CF'] = final_gen['Daily_MWh'] / final_gen['Daily_Potential_MWh']

    final_weather = weather_df.groupby(['Region', 'Period'])[[TARGET_WEATHER]].mean().reset_index()

    final_df = pd.merge(final_gen, final_weather, on=['Region', 'Period'])
    regions = final_df['Region'].unique()

    # 7. Visualization
    colors = {'Northern Europe': '#1f77b4', 'Southern Europe': '#ff7f0e'}
    fig, ax = plt.subplots(figsize=(11, 7))

    for r in regions:
        r_data = final_df[final_df['Region'] == r].dropna(subset=[TARGET_WEATHER, 'CF'])
        x = r_data[TARGET_WEATHER].values
        y = r_data['CF'].values
        n_samples = len(x)
        
        dot_size = 20 if TIMEFRAME == 'Daily' else 70
        dot_alpha = 0.4 if TIMEFRAME == 'Daily' else 0.7
        edge_style = 'none' if TIMEFRAME == 'Daily' else 'black'
        
        ax.scatter(x, y, color=colors.get(r, 'gray'), alpha=dot_alpha, s=dot_size, edgecolors=edge_style)
        
        if n_samples >= 3:
            slope, intercept, _, _, _ = stats.linregress(x, y)
            x_line = np.array([x.min(), x.max()])
            y_line = slope * x_line + intercept
            
            res_p = stats.pearsonr(x, y)
            ci_p = res_p.confidence_interval(confidence_level=0.95)
            
            p_val_str = "<0.001" if res_p.pvalue < 0.001 else f"{res_p.pvalue:.3f}"
            label_text = (f"{r} (N={n_samples})\n"
                          f"r = {res_p.statistic:.2f} (p {p_val_str})\n"
                          f"95% CI: [{ci_p.low:.2f}, {ci_p.high:.2f}]")
            
            ax.plot(x_line, y_line, color=colors.get(r, 'gray'), linestyle='--', linewidth=2.5, label=label_text)
        else:
            ax.plot([], [], ' ', label=f"{r} (N={n_samples}, Insufficient Data)")

    clean_var_name = TARGET_WEATHER.replace('_', ' ').title()
    ax.set_title(f"Pearson Correlation: {TIMEFRAME} Capacity Factor vs. {clean_var_name} ({TARGET_TECH})", fontsize=14, fontweight='bold')
    ax.set_xlabel(f"Average {clean_var_name}", fontsize=12)
    ax.set_ylabel("Capacity Factor (CF)", fontsize=12)
    
    ax.legend(title="Region & Pearson Stats", loc='best', fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()

    st.pyplot(
    fig,
    use_container_width=True
)

if not all([tech, weather, timeframe]):
    st.info("Please select an option for Technology, Weather Variable, and Timeframe to display the chart.")
    st.stop()

execute_fast_pipeline()
