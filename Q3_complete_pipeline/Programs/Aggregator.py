#AI assisted code.
import os
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# CONFIGURATION
# ==========================================
GEN_DIR = "Daily_Generation_MWh"
CAP_DIR = "Final_Validated_Capacity"

OUT_GEN_FILE = "European_Daily_Generation_2023_2025.csv"
OUT_CAP_FILE = "European_Validated_Capacity_2023_2025.csv"

NORTHERN_EUROPE = ['Denmark', 'Sweden', 'Finland', 'Lithuania', 'Ireland', 'Estonia', 'Latvia', 'Norway']
SOUTHERN_EUROPE = ['Portugal', 'Italy', 'Spain', 'Serbia', 'Croatia', 'Bosnia and Herzegovina', 'Greece', 'Montenegro', 'Slovenia', 'North Macedonia']

TECHS = ['Bioenergy', 'Hydro', 'Wind', 'Solar']

def get_region(country):
    if country in NORTHERN_EUROPE: return 'Northern Europe'
    if country in SOUTHERN_EUROPE: return 'Southern Europe'
    return 'Unknown'

def aggregate_capacity():
    print(f"--- Aggregating Capacity Data from '{CAP_DIR}/' ---")
    cap_list = []
    
    if not os.path.exists(CAP_DIR):
        print(f"[!] Error: Directory '{CAP_DIR}' not found.")
        return

    for file in os.listdir(CAP_DIR):
        if file.endswith(".csv"):
            # Extract the strict country name from the filename (e.g., "Spain_Capacity_2023_2025.csv" -> "Spain")
            country = file.split("_Capacity")[0]
            
            df = pd.read_csv(os.path.join(CAP_DIR, file))
            
            # Enforce strict column standardization
            df['Country'] = country
            df['Region'] = get_region(country)
            
            # Reorder columns for readability
            cols = ['Region', 'Country', 'Year'] + [t for t in TECHS if t in df.columns]
            cap_list.append(df[cols])
            
    if cap_list:
        all_cap = pd.concat(cap_list, ignore_index=True)
        # Sort geographically and chronologically
        all_cap = all_cap.sort_values(by=['Region', 'Country', 'Year'])
        all_cap.to_csv(OUT_CAP_FILE, index=False)
        print(f"✓ Saved {len(all_cap)} rows to {OUT_CAP_FILE}")
    else:
        print("[!] No capacity CSVs found.")

def aggregate_generation():
    print(f"\n--- Aggregating Generation Data from '{GEN_DIR}/' ---")
    gen_list = []
    
    if not os.path.exists(GEN_DIR):
        print(f"[!] Error: Directory '{GEN_DIR}' not found.")
        return

    for file in os.listdir(GEN_DIR):
        if file.endswith(".csv"):
            country = file.split("_Generation")[0]
            df = pd.read_csv(os.path.join(GEN_DIR, file))

            # 1. Standardize Timestamps
            # If a country (like Finland) uses hourly 'Time (Local)', convert it to YYYY-MM-DD
            if 'Time (Local)' in df.columns:
                df['Date'] = pd.to_datetime(df['Time (Local)'], utc=True).dt.strftime('%Y-%m-%d')
                # Sum the 24 hourly rows into 1 daily row for the specific technologies
                df = df.groupby('Date')[TECHS].sum().reset_index()
            elif 'Date' in df.columns:
                # Ensure existing dates are safely formatted strings
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

            # 2. Append Geographic Metadata
            df['Country'] = country
            df['Region'] = get_region(country)
            
            # 3. Reorder and secure columns
            cols = ['Region', 'Country', 'Date'] + [t for t in TECHS if t in df.columns]
            gen_list.append(df[cols])
            
    if gen_list:
        all_gen = pd.concat(gen_list, ignore_index=True)
        all_gen = all_gen.sort_values(by=['Region', 'Country', 'Date'])
        all_gen.to_csv(OUT_GEN_FILE, index=False)
        print(f"✓ Saved {len(all_gen)} rows to {OUT_GEN_FILE}")
    else:
        print("[!] No generation CSVs found.")

if __name__ == "__main__":
    aggregate_capacity()
    aggregate_generation()
    print("\nAggregation complete. You can now use the master files for visualization.")
