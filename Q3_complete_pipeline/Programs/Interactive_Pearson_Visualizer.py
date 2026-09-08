import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURATION
# ==========================================
GEN_DIR = "Daily_Generation_MWh"
CAP_DIR = "Final_Validated_Capacity"
WEATHER_FILE = "Regional_Weighted_Weather_2023_2025.csv"

NORTHERN_EUROPE = ['Denmark', 'Sweden', 'Finland', 'Lithuania', 'Ireland', 'Estonia', 'Latvia', 'Norway']
SOUTHERN_EUROPE = ['Portugal', 'Italy', 'Spain', 'Serbia', 'Croatia', 'Bosnia and Herzegovina', 'Greece', 'Montenegro', 'Slovenia', 'North Macedonia']

TECHS = ['Wind', 'Solar', 'Hydro', 'Bioenergy']

WEATHER_MAPPING = {
    'Wind': ['Wind_Speed_100m', 'Wind_Speed_100m_Cubed', 'Wind_Gusts_10m_Max', 'Temperature_2m_Max', 'Apparent_Temperature_Min'],
    'Solar': ['Shortwave_Radiation_Sum', 'Temperature_2m_Max', 'Apparent_Temperature_Min', 'Snow_Depth'],
    'Hydro': ['Precipitation_Sum', 'Snow_Depth', 'Temperature_2m_Max', 'Apparent_Temperature_Min'],
    'Bioenergy': ['Temperature_2m_Max', 'Apparent_Temperature_Min']
}

def get_region(country):
    if country in NORTHERN_EUROPE: return 'Northern Europe'
    if country in SOUTHERN_EUROPE: return 'Southern Europe'
    return 'Unknown'

def load_and_process_data():
    print("Loading Capacity Data...")
    cap_list = []
    for file in os.listdir(CAP_DIR):
        if file.endswith(".csv"):
            country = file.split("_Capacity")[0]
            df = pd.read_csv(os.path.join(CAP_DIR, file))
            df['Country'] = country
            cap_list.append(df)
    all_cap = pd.concat(cap_list, ignore_index=True)

    print("Loading Generation Data...")
    gen_list = []
    for file in os.listdir(GEN_DIR):
        if file.endswith(".csv"):
            country = file.split("_Generation")[0]
            df = pd.read_csv(os.path.join(GEN_DIR, file))

            if 'Time (Local)' in df.columns:
                df['Date'] = pd.to_datetime(df['Time (Local)'], utc=True).dt.strftime('%Y-%m-%d')
                df = df.groupby('Date')[TECHS].sum().reset_index()
            elif 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

            df['Country'] = country
            gen_list.append(df)
            
    all_gen = pd.concat(gen_list, ignore_index=True)
    all_gen['Year'] = pd.to_datetime(all_gen['Date']).dt.year

    print("Melting and Merging Datasets...")
    gen_melt = all_gen.melt(id_vars=['Country', 'Date', 'Year'], value_vars=TECHS, var_name='Technology', value_name='Daily_MWh')
    cap_melt = all_cap.melt(id_vars=['Country', 'Year'], value_vars=TECHS, var_name='Technology', value_name='Capacity_MW')

    merged = pd.merge(gen_melt, cap_melt, on=['Country', 'Year', 'Technology'], how='left')
    merged = merged.dropna(subset=['Daily_MWh'])

    merged['Daily_Potential_MWh'] = merged['Capacity_MW'] * 24
    merged['Region'] = merged['Country'].apply(get_region)

    regional_daily = merged.groupby(['Region', 'Technology', 'Date', 'Year']).agg({
        'Daily_MWh': 'sum',
        'Daily_Potential_MWh': 'sum'
    }).reset_index()

    regional_daily['Month'] = pd.to_datetime(regional_daily['Date']).dt.strftime('%Y-%m')

    weather = pd.read_csv(WEATHER_FILE)
    weather['Date'] = pd.to_datetime(weather['Date']).dt.strftime('%Y-%m-%d')

    return regional_daily, weather

def interactive_pearson_plotter(regional_daily, weather):
    while True:
        print("\n" + "="*60)
        print("  INTERACTIVE PEARSON CORRELATION GRAPHS")
        print("="*60)
        print("Available Technologies: Wind, Solar, Hydro, Bioenergy")
        tech = input("Enter Energy Source (or 'q' to quit): ").strip().title()
        
        if tech.lower() == 'q':
            break
        if tech not in TECHS:
            print("[!] Invalid source. Defaulting to Wind.")
            tech = 'Wind'

        print("\nAvailable Timeframes: Daily (N≈1095), Monthly (N=36)")
        timeframe = input("Enter Timeframe (default: Monthly): ").strip().title()
        if timeframe not in ['Daily', 'Monthly']: 
            timeframe = 'Monthly'

        tech_gen = regional_daily[regional_daily['Technology'] == tech]

        # Dynamically aggregate based on user selection
        if timeframe == 'Monthly':
            agg_gen = tech_gen.groupby(['Region', 'Month']).agg({'Daily_MWh':'sum', 'Daily_Potential_MWh':'sum'}).reset_index()
            agg_gen = agg_gen.rename(columns={'Month': 'Period'})
            weather['Period'] = pd.to_datetime(weather['Date']).dt.strftime('%Y-%m')
        else:
            agg_gen = tech_gen.groupby(['Region', 'Date']).agg({'Daily_MWh':'sum', 'Daily_Potential_MWh':'sum'}).reset_index()
            agg_gen = agg_gen.rename(columns={'Date': 'Period'})
            weather['Period'] = weather['Date']

        agg_gen['CF'] = agg_gen['Daily_MWh'] / agg_gen['Daily_Potential_MWh']

        weather_vars = WEATHER_MAPPING.get(tech, ['Temperature_2m_Max'])
        available_w_vars = [v for v in weather_vars if v in weather.columns]
        
        agg_weather = weather.groupby(['Region', 'Period'])[available_w_vars].mean().reset_index()
        final_df = pd.merge(agg_gen, agg_weather, on=['Region', 'Period'])
        regions = final_df['Region'].unique()
        
        colors = {'Northern Europe': '#1f77b4', 'Southern Europe': '#ff7f0e', 'Unknown': '#2ca02c'}

        for w_var in available_w_vars:
            plt.figure(figsize=(11, 7))
            
            for r in regions:
                r_data = final_df[final_df['Region'] == r].dropna(subset=[w_var, 'CF'])
                x = r_data[w_var].values
                y = r_data['CF'].values
                n_samples = len(x)
                
                # Base scatter plot. Reduce dot size and opacity for Daily to prevent visual clustering.
                dot_size = 20 if timeframe == 'Daily' else 70
                dot_alpha = 0.4 if timeframe == 'Daily' else 0.7
                plt.scatter(x, y, color=colors.get(r, 'gray'), alpha=dot_alpha, s=dot_size, edgecolors='black' if timeframe == 'Monthly' else 'none')
                
                # Pearson and Regression require at least 3 points
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
                    
                    plt.plot(x_line, y_line, color=colors.get(r, 'gray'), linestyle='--', linewidth=2.5, label=label_text)
                else:
                    plt.plot([], [], ' ', label=f"{r} (N={n_samples}, Insufficient Data)")

            clean_var_name = w_var.replace('_', ' ').title()
            plt.title(f"Pearson Correlation: {timeframe} Capacity Factor vs. {clean_var_name} ({tech})", fontsize=14, fontweight='bold')
            plt.xlabel(f"Average {clean_var_name}", fontsize=12)
            plt.ylabel("Capacity Factor (CF)", fontsize=12)
            
            plt.legend(title="Region & Pearson Stats", loc='best', fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            print(f"-> Generating plot for {clean_var_name}...")
            plt.show()

if __name__ == "__main__":
    reg_daily, w_data = load_and_process_data()
    interactive_pearson_plotter(reg_daily, w_data)
    print("\nVisualizer closed. Goodbye!")