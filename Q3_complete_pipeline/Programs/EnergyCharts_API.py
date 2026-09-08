import requests
import pandas as pd
import time
import os

def main():
    countries = {
        'Denmark': 'dk', 'Sweden': 'se', 'Finland': 'fi', 
        'Lithuania': 'lt', 'Ireland': 'ie', 'Estonia': 'ee', 'Latvia': 'lv', 
        'Norway': 'no', 'Portugal': 'pt', 'Italy': 'it', 'Spain': 'es', 
        'Serbia': 'rs', 'Croatia': 'hr', 'Bosnia and Herzegovina': 'ba', 
        'Greece': 'gr', 'Montenegro': 'me', 'Slovenia': 'si', 'North Macedonia': 'mk'
    }

    years = [2023, 2024, 2025]
    
    gen_output_dir = "Renewable_Generation_By_Country"
    cap_output_dir = "Installed_Capacity_By_Country"
    
    os.makedirs(gen_output_dir, exist_ok=True)
    os.makedirs(cap_output_dir, exist_ok=True)

    # ---------------------------------------------------------
    # TAXONOMY MAPPING
    # ---------------------------------------------------------
    gen_target_techs = ['Biomass', 'Waste', 'Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage', 'Solar', 'Wind onshore', 'Wind offshore']
    cap_target_techs = ['Biomass', 'Waste', 'Hydro', 'Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage', 'Solar DC', 'Solar AC', 'Wind onshore', 'Wind offshore']

    gen_agg_map = {
        'Bioenergy': ['Biomass', 'Waste'],
        'Hydro': ['Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage'],
        'Wind': ['Wind onshore', 'Wind offshore'],
        'Solar': ['Solar']
    }
    
    cap_agg_map = {
        'Bioenergy': ['Biomass', 'Waste'],
        'Hydro': ['Hydro', 'Hydro Run-of-River', 'Hydro water reservoir', 'Hydro pumped storage'],
        'Wind': ['Wind onshore', 'Wind offshore'],
        'Solar': ['Solar DC', 'Solar AC'] 
    }
    
    FINAL_TECHS = ['Bioenergy', 'Hydro', 'Wind', 'Solar']

    def aggregate_technologies(df, is_capacity=False):
        """Fuses subcategories, normalizes the column structure, and handles missing data."""
        time_col = 'Year' if is_capacity else 'Time (Local)'
        mapping = cap_agg_map if is_capacity else gen_agg_map
        
        # 1. Fuse subcategories (e.g., Biomass + Waste -> Bioenergy)
        for final_tech, sub_techs in mapping.items():
            if final_tech == 'Solar': continue
            existing_cols = [col for col in sub_techs if col in df.columns]
            if existing_cols:
                df[final_tech] = df[existing_cols].sum(axis=1, min_count=1)
                
        # 2. Process Solar explicitly to prevent AC/DC double counting
        if 'Solar DC' in df.columns and 'Solar AC' in df.columns:
            df['Solar'] = df['Solar DC'].fillna(df['Solar AC'])
        elif 'Solar DC' in df.columns:
            df['Solar'] = df['Solar DC']
        elif 'Solar AC' in df.columns:
            df['Solar'] = df['Solar AC']
            
        # 3. Unit Conversion for Capacity
        if is_capacity:
            for tech in FINAL_TECHS:
                if tech in df.columns:
                    df[tech] = df[tech] * 1000.0
                    
        # 4. NORMALIZATION: Force all 4 columns to exist
        for tech in FINAL_TECHS:
            if tech not in df.columns:
                df[tech] = 0.0 # Country lacks the infrastructure completely
                
        # 5. Missing Row & NaN Handling
        if is_capacity:
            # Force all years (2023, 2024, 2025) to exist in the dataframe
            all_years = pd.DataFrame({'Year': years})
            df = pd.merge(all_years, df, on='Year', how='left')
            # Fill missing capacity values (NaNs) with 0.0
            df[FINAL_TECHS] = df[FINAL_TECHS].fillna(0.0)
        else:
            # For generation, missing columns got 0.0 above. 
            # We DO NOT run fillna(0.0) on existing columns to preserve telemetry NaNs.
            pass

        # Return strictly the 5 requested columns in exact order
        return df[[time_col] + FINAL_TECHS]

    print("--- Starting Energy-Charts API Fetch (Hardened & Normalized) ---")
    
    for country, code in countries.items():
        print(f"\nProcessing {country} ({code.upper()})...")
        
        # ==========================================
        # 1. Fetch Installed Capacity
        # ==========================================
        cap_url = f"https://api.energy-charts.info/v2/installed_power?country={code}&time_step=yearly"
        try:
            cap_response = requests.get(cap_url)
            if cap_response.status_code == 200:
                payload = cap_response.json()
                data_points = payload.get('data', [])
                
                cap_rows = []
                if data_points:
                    series_info = payload.get('series', [])
                    id_to_name = {s['id']: s['name'] for s in series_info}
                    
                    for dp in data_points:
                        year_str = dp.get('timestamp', '')[:4]
                        if year_str.isdigit() and int(year_str) in years:
                            row = {'Year': int(year_str)}
                            for s_id, val in dp.get('values', {}).items():
                                name = id_to_name.get(s_id)
                                if name in cap_target_techs:
                                    row[name] = val
                            cap_rows.append(row)
                            
                df_cap = pd.DataFrame(cap_rows) if cap_rows else pd.DataFrame(columns=['Year'])
                
                # Normalize and save
                df_cap = aggregate_technologies(df_cap, is_capacity=True)
                file_path = os.path.join(cap_output_dir, f"{country}_Capacity_2023_2025.csv")
                df_cap.to_csv(file_path, index=False)
                print(f"  -> Saved {country} Capacity data (Normalized).")
                
            else:
                print(f"  [Error] Capacity fetch failed with HTTP {cap_response.status_code}")
        except Exception as e:
            print(f"  [Error] Capacity fetch exception: {str(e)}")
            
        time.sleep(1.5)
        
        # ==========================================
        # 2. Fetch Daily Generation
        # ==========================================
        country_yearly_dfs = []
        for year in years:
            url = f"https://api.energy-charts.info/v2/public_power?country={code}&start={year}-01-01&end={year}-12-31"
            
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    response = requests.get(url)
                    
                    if response.status_code == 429:
                        wait_time = 15 * (attempt + 1)
                        print(f"  [Rate Limited] Pausing for {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                        
                    if response.status_code != 200:
                        break 
                        
                    payload = response.json()
                    data_points = payload.get('data', [])
                    if not data_points:
                        break
                    
                    series_info = payload.get('series', [])
                    id_to_name = {s['id']: s['name'] for s in series_info}
                    
                    rows = []
                    for dp in data_points:
                        row = {'Time (Local)': dp.get('timestamp')}
                        for s_id, val in dp.get('values', {}).items():
                            name = id_to_name.get(s_id)
                            if name in gen_target_techs:
                                row[name] = val
                        rows.append(row)
                        
                    country_yearly_dfs.append(pd.DataFrame(rows))
                    print(f"  [Success] Generation {year} fetched.")
                    break 
                    
                except Exception as e:
                    time.sleep(5)
            time.sleep(1.5) 

        if country_yearly_dfs:
            df_country_all = pd.concat(country_yearly_dfs, ignore_index=True)
            df_country_all.sort_values('Time (Local)', inplace=True)
            
            # Normalize and save
            df_country_all = aggregate_technologies(df_country_all, is_capacity=False)
            file_path = os.path.join(gen_output_dir, f"{country}_Generation_2023_2025.csv")
            df_country_all.to_csv(file_path, index=False)
            print(f"  -> Saved {country} Generation data (Normalized).")
        else:
            print(f"  -> No generation data found for {country}.")

if __name__ == "__main__":
    main()