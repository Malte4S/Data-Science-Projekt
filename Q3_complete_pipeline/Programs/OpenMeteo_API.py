#AI assisted code.
import pandas as pd
import requests
import os
import time
import sys
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = "European_Renewable_Clusters.csv"
OUTPUT_FILE = "European_Weather_Data_2023_2025.csv"
TARGET_YEARS = [2023, 2024, 2025]

DAILY_VARS = [
    "shortwave_radiation_sum", 
    "temperature_2m_max", 
    "wind_gusts_10m_max", 
    "precipitation_sum", 
    "apparent_temperature_min"
]

HOURLY_VARS = [
    "wind_speed_100m", 
    "snow_depth"
]

def load_coordinates():
    print(f"Reading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    # We drop the political geography entirely. 
    # We only care: Did a grid square contain ANY active infrastructure in a specific year?
    unique_coords = df[['Year', 'Latitude_Round', 'Longitude_Round']].drop_duplicates()
    return unique_coords

def get_completed_coordinates():
    if not os.path.exists(OUTPUT_FILE):
        return set()
    
    try:
        df = pd.read_csv(OUTPUT_FILE, usecols=['time', 'Lat_Rounded', 'Lon_Rounded'])
        df['Fetched_Year'] = df['time'].str[:4].astype(int)
        
        completed_df = df[['Fetched_Year', 'Lat_Rounded', 'Lon_Rounded']].drop_duplicates()
        
        completed = set(
            (int(year), round(lat, 2), round(lon, 2)) 
            for year, lat, lon in zip(
                completed_df['Fetched_Year'], 
                completed_df['Lat_Rounded'], 
                completed_df['Lon_Rounded']
            )
        )
        return completed
    except Exception as e:
        print(f"Could not read existing progress: {e}")
        return set()

def fetch_and_aggregate_weather(row):
    year = int(row['Year'])
    lat, lon = row['Latitude_Round'], row['Longitude_Round']
    
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARS),
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto" 
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        
        if response.status_code == 429:
            if attempt == 0:
                print(f"  [Rate Limited] Minutely limit hit. Pausing for 65s...")
                time.sleep(65)
                continue
            elif attempt == 1:
                print(f"  [Rate Limited] Hourly limit hit. Pausing for 300s...")
                time.sleep(300)
                continue
            else:
                return "DAILY_LIMIT"
                
        if response.status_code != 200:
            print(f"  [Error] HTTP {response.status_code} at {lat}, {lon}")
            return "ERROR"
            
        data = response.json()
        
        df_daily = pd.DataFrame(data.get('daily', {}))
        if df_daily.empty:
            return "ERROR"
            
        df_hourly = pd.DataFrame(data.get('hourly', {}))
        if not df_hourly.empty:
            df_hourly['date'] = df_hourly['time'].str[:10]
            df_hourly['wind_speed_100m_cubed'] = df_hourly['wind_speed_100m'] ** 3
            
            daily_agg = df_hourly.groupby('date').agg({
                'wind_speed_100m': 'mean',
                'wind_speed_100m_cubed': 'mean',
                'snow_depth': 'mean' 
            }).reset_index()
            
            df_daily = pd.merge(df_daily, daily_agg, left_on='time', right_on='date', how='left')
            df_daily.drop(columns=['date'], inplace=True)
        
        # Output format is now purely geographic and temporal
        df_daily.insert(0, 'Lat_Rounded', lat)
        df_daily.insert(1, 'Lon_Rounded', lon)
        
        header = not os.path.exists(OUTPUT_FILE)
        df_daily.to_csv(OUTPUT_FILE, mode='a', index=False, header=header)
        
        return "SUCCESS"

def main():
    coords_df = load_coordinates()
    completed = get_completed_coordinates()
    
    total_requests = len(coords_df)
    requests_processed = len(completed)
    
    print("\n--- Starting Fetch Process (Pure Geographic Grid) ---")
    print(f"Found {total_requests} unique (Year -> Coordinate) physical targets.")
    print(f"Progress loaded: {requests_processed} items already secured in CSV.")
    
    for year in TARGET_YEARS:
        year_data = coords_df[coords_df['Year'] == year]
        if year_data.empty: continue
        
        print(f"\n=========================================")
        print(f" FETCHING METEOROLOGY FOR {year}")
        print(f"=========================================")
        
        remaining = [
            (int(r['Year']), round(r['Latitude_Round'], 2), round(r['Longitude_Round'], 2)) 
            for _, r in year_data.iterrows() 
            if (int(r['Year']), round(r['Latitude_Round'], 2), round(r['Longitude_Round'], 2)) not in completed
        ]
        
        if not remaining:
            continue
            
        print(f"Processing {len(remaining)} unique physical coordinates...")
        
        for index, row in year_data.iterrows():
            coord_tuple = (int(row['Year']), round(row['Latitude_Round'], 2), round(row['Longitude_Round'], 2))
            
            if coord_tuple in completed:
                continue
                
            status = fetch_and_aggregate_weather(row)
            
            if status == "DAILY_LIMIT":
                print("\n" + "="*60)
                print("🛑 DAILY API LIMIT REACHED (HTTP 429)!")
                print(f"Progress safely secured in '{OUTPUT_FILE}'.")
                print("Restart this script tomorrow. It will resume exactly where it left off.")
                print("="*60)
                sys.exit(0)
                
            elif status == "SUCCESS":
                requests_processed += 1
                print(f"  -> {coord_tuple[1]}, {coord_tuple[2]} Saved. ({requests_processed}/{total_requests} Total)")
                time.sleep(1.5) 
            else:
                print(f"  -> {coord_tuple[1]}, {coord_tuple[2]} Failed. Skipping.")
                time.sleep(2.0)
                    
    print(f"\nAll operations finished! Dataset is complete in {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
