#AI assisted code.
import os
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
INPUT_FILES = {
    'Bioenergy': 'European_Bioenergy_Data.xlsx',
    'Hydro': 'European_Hydro_Data.xlsx',
    'Solar': 'European_Solar_Data.xlsx',
    'Wind': 'European_Wind_Data.xlsx' 
}

NORTHERN_EUROPE = ['Denmark', 'Sweden', 'Finland', 'Lithuania', 'Ireland', 'Estonia', 'Latvia', 'Norway']
SOUTHERN_EUROPE = ['Portugal', 'Italy', 'Spain', 'Serbia', 'Croatia', 'Bosnia and Herzegovina', 'Greece', 'Montenegro', 'Slovenia', 'North Macedonia']

TARGET_YEARS = [2023, 2024, 2025]

def get_region(country):
    if country in NORTHERN_EUROPE: return 'Northern Europe'
    if country in SOUTHERN_EUROPE: return 'Southern Europe'
    return None

def process_trackers():
    all_data = []
    
    print("--- Starting Yearly Equal-Area Clustering ---")
    for tech, filename in INPUT_FILES.items():
        if not os.path.exists(filename):
            print(f"[Skipping] {filename} not found.")
            continue
            
        print(f"Processing {tech}...")
        df = pd.read_excel(filename)
        
        # --- EQUAL-AREA COSINE CORRECTION ---
        df['Latitude_Round'] = df['Latitude'].round(0)
        lat_radians = np.radians(df['Latitude_Round'])
        lon_step = 1.0 / np.clip(np.cos(lat_radians), 0.01, 1.0)
        df['Longitude_Round'] = (df['Longitude'] / lon_step).round(0) * lon_step
        df['Longitude_Round'] = df['Longitude_Round'].round(2)
        
        # --- YEARLY FILTERING ---
        for year in TARGET_YEARS:
            # Condition: Built before/during the target year, and hasn't retired yet
            started = df['Start Year'].isna() | (df['Start Year'] <= year)
            not_retired = df['Retired Year'].isna() | (df['Retired Year'] >= year)
            
            active_df = df[started & not_retired].copy()
            if active_df.empty:
                continue
                
            active_df['Technology'] = tech
            active_df['Year'] = year
            all_data.append(active_df)

    if not all_data:
        print("No valid data found.")
        return pd.DataFrame()

    master_df = pd.concat(all_data, ignore_index=True)
    
    # --- IMPLICIT SPLIT & AGGREGATION ---
    # Grouping directly by Country alongside coordinates ensures border-spanning 
    # capacities separate cleanly into independent national records.
    clusters = master_df.groupby(['Technology', 'Country', 'Year', 'Latitude_Round', 'Longitude_Round']).agg(
        Total_Capacity=('Capacity (MW)', 'sum')
    ).reset_index()
    
    clusters['Region'] = clusters['Country'].apply(get_region)
    clusters = clusters.dropna(subset=['Region']) 
    
    # Enforce strict formatting and column order
    clusters = clusters[['Region', 'Technology', 'Country', 'Year', 'Latitude_Round', 'Longitude_Round', 'Total_Capacity']]
    clusters['Total_Capacity'] = clusters['Total_Capacity'].round(1)
    
    # Sort for readability (Largest capacities at top)
    clusters = clusters.sort_values(by=['Region', 'Technology', 'Country', 'Year', 'Total_Capacity'], ascending=[True, True, True, True, False])
    
    return clusters

if __name__ == "__main__":
    final_clusters = process_trackers()
    
    if not final_clusters.empty:
        csv_out = "European_Renewable_Clusters.csv"
        final_clusters.to_csv(csv_out, index=False)
        print(f"\n✓ Master CSV saved to: {csv_out}")
            
        print("*** ALL EXPORTS COMPLETE ***")
