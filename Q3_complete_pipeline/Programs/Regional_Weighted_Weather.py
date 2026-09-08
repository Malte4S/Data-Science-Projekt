#AI assisted code.
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def build_regional_weather():
    print("--- Starting Regional Weather Weighting ---")
    
    # 1. Load the data 
    clusters = pd.read_csv("European_Renewable_Clusters.csv")
    weather = pd.read_csv("European_Weather_Data_2023_2025.csv")
    
    # 2. Extract Year from weather to precisely match the clustered time-travel logic
    weather['Date'] = weather['time'].str[:10]
    weather['Year'] = weather['Date'].str[:4].astype(int)
    
    # 3. Pivot Clusters by Technology
    pivot_cols = ['Region', 'Year', 'Latitude_Round', 'Longitude_Round']
    cluster_pivot = clusters.groupby(pivot_cols + ['Technology'])['Total_Capacity'].sum().unstack(fill_value=0).reset_index()
    
    techs = [c for c in ['Wind', 'Solar', 'Hydro', 'Bioenergy'] if c in cluster_pivot.columns]
    cluster_pivot['Total_Capacity'] = cluster_pivot[techs].sum(axis=1)
    
    # 4. Merge Weather with Cluster Weights
    merged = pd.merge(
        weather, 
        cluster_pivot, 
        left_on=['Lat_Rounded', 'Lon_Rounded', 'Year'], 
        right_on=['Latitude_Round', 'Longitude_Round', 'Year'],
        how='inner'
    )
    
    # 5. Apply the Technology-Specific Mathematical Weights
    if 'Wind' in merged.columns:
        merged['w_wind'] = merged['wind_speed_100m'] * merged['Wind']
        merged['w_wind_cube'] = merged['wind_speed_100m_cubed'] * merged['Wind']
        merged['w_gusts'] = merged['wind_gusts_10m_max'] * merged['Wind']
        
    if 'Solar' in merged.columns:
        merged['w_solar'] = merged['shortwave_radiation_sum'] * merged['Solar']
        
    if 'Hydro' in merged.columns:
        merged['w_precip'] = merged['precipitation_sum'] * merged['Hydro']
        merged['w_snow'] = merged['snow_depth'] * merged['Hydro']
        
    merged['w_temp'] = merged['temperature_2m_max'] * merged['Total_Capacity']
    merged['w_app_temp'] = merged['apparent_temperature_min'] * merged['Total_Capacity']
    
    # 6. Sum the weighted numerators by Region and Date
    agg_dict = {t: 'sum' for t in techs}
    agg_dict['Total_Capacity'] = 'sum'
    
    weight_cols = [c for c in merged.columns if c.startswith('w_')]
    for wc in weight_cols:
        agg_dict[wc] = 'sum'
        
    regional = merged.groupby(['Region', 'Date']).agg(agg_dict).reset_index()
    
    # 7. Divide by the exact technological denominator
    if 'Wind' in regional.columns:
        safe_wind = regional['Wind'].replace(0, pd.NA) 
        regional['Wind_Speed_100m'] = (regional['w_wind'] / safe_wind).round(2)
        regional['Wind_Speed_100m_Cubed'] = (regional['w_wind_cube'] / safe_wind).round(2)
        regional['Wind_Gusts_10m_Max'] = (regional['w_gusts'] / safe_wind).round(2)
        
    if 'Solar' in regional.columns:
        safe_solar = regional['Solar'].replace(0, pd.NA)
        regional['Shortwave_Radiation_Sum'] = (regional['w_solar'] / safe_solar).round(2)
        
    if 'Hydro' in regional.columns:
        safe_hydro = regional['Hydro'].replace(0, pd.NA)
        regional['Precipitation_Sum'] = (regional['w_precip'] / safe_hydro).round(2)
        regional['Snow_Depth'] = (regional['w_snow'] / safe_hydro).round(2)
        
    safe_total = regional['Total_Capacity'].replace(0, pd.NA)
    regional['Temperature_2m_Max'] = (regional['w_temp'] / safe_total).round(2)
    regional['Apparent_Temperature_Min'] = (regional['w_app_temp'] / safe_total).round(2)
    
    # 8. Cleanup and Export (BUG FIX: explicitly ignore 'Region' and 'Date' in the dynamic loop)
    ignore_cols = techs + ['Total_Capacity', 'Region', 'Date']
    final_cols = ['Region', 'Date'] + [c for c in regional.columns if c[0].isupper() and c not in ignore_cols]
    
    final_df = regional[final_cols]
    
    final_df.to_csv("Regional_Weighted_Weather_2023_2025.csv", index=False)
    print("✓ Successfully calculated technology-specific weighted weather.")
    print("✓ Saved to 'Regional_Weighted_Weather_2023_2025.csv'")
    
if __name__ == "__main__":
    build_regional_weather()
