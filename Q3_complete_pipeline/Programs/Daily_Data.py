import os
import glob
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

INPUT_DIR = "Renewable_Generation_By_Country"
OUTPUT_DIR = "Daily_Generation_MWh"
TARGET_TECHS = ['Bioenergy', 'Hydro', 'Wind', 'Solar']

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    if not files:
        print(f"No CSV files found in '{INPUT_DIR}'.")
        return

    print("--- Starting Simplified Sub-Daily to Daily MWh Normalization ---")
    
    for file_path in files:
        filename = os.path.basename(file_path)
        country = filename.split('_')[0]
        
        df = pd.read_csv(file_path)
        if df.empty or len(df) < 2:
            continue
            
        # 1. Parse timestamps
        # Use UTC ONLY for math to bypass Daylight Saving Time overlaps/skips
        df['UTC'] = pd.to_datetime(df['Time (Local)'], utc=True)
        df = df.sort_values('UTC').reset_index(drop=True)
        
        # Extract the Year and Date strictly from the Local Time string
        df['Year'] = df['Time (Local)'].str[:4].astype(int)
        df['Date'] = df['Time (Local)'].str[:10]
        
        # 2. Determine the static interval per local year
        interval_map = {}
        for year, group in df.groupby('Year'):
            if len(group) > 1:
                # Mode returns the most common gap. Extract total seconds and convert to hours.
                mode_seconds = group['UTC'].diff().dt.total_seconds().mode()[0]
                interval_map[year] = mode_seconds / 3600.0
            else:
                interval_map[year] = 1.0 # Fallback 
                
        # 3. Map the calculated interval back to every row based on its local year
        df['Interval_Hours'] = df['Year'].map(interval_map)
        
        # 4. Convert MW to MWh
        for tech in TARGET_TECHS:
            if tech in df.columns:
                df[tech] = df[tech] * df['Interval_Hours']
                
        # 5. Group into Daily totals and enforce the 22-Hour Safety Threshold
        agg_funcs = {tech: 'sum' for tech in TARGET_TECHS if tech in df.columns}
        agg_funcs['Interval_Hours'] = 'sum'
        
        daily_df = df.groupby('Date').agg(agg_funcs).reset_index()
        
        # If a day recorded less than 22 hours of local data, discard it
        invalid_days = daily_df['Interval_Hours'] < 22.0
        for tech in TARGET_TECHS:
            if tech in daily_df.columns:
                daily_df.loc[invalid_days, tech] = pd.NA
                
        # 6. Final Cleanup
        daily_df.insert(0, 'Country', country)
        daily_df = daily_df.drop(columns=['Interval_Hours'])
        
        out_path = os.path.join(OUTPUT_DIR, filename)
        daily_df.to_csv(out_path, index=False)
        
        intervals_detected = [f"{year}: {int(hrs * 60)}m" for year, hrs in interval_map.items()]
        print(f"✓ Processed {country} | Intervals -> {', '.join(intervals_detected)}")
        
    print(f"\nAll files correctly aggregated and stored in '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()