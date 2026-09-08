import pandas as pd

def generate_capacity_estimates():
    # Map your 4 target indices to the respective simplified GEM files
    tracker_files = {
        'Hydro': 'European_Hydro_Data.xlsx',
        'Wind': 'European_Wind_Data.xlsx',
        'Solar': 'European_Solar_Data.xlsx',
        'Bioenergy': 'European_Bioenergy_Data.xlsx'
    }
    
    target_years = [2023, 2024, 2025]
    all_results = []
    
    for tech, filepath in tracker_files.items():
        print(f"Aggregating {tech} data from {filepath}...")
        df = pd.read_excel(filepath)
        
        for year in target_years:
            # 1. START YEAR LOGIC
            # If a plant was commissioned in 2023, it generated power in 2023, so we count it.
            # If the Start Year is NaN, it is an active/retired plant with an unknown historical 
            # build date. We safely assume it was built before our 2023-2025 window.
            started = df['Start Year'].isna() | (df['Start Year'] <= year)
            
            # 2. RETIRED YEAR LOGIC
            # If a plant retired in 2023, it still contributed to the grid for part of that year, 
            # so we keep it in the 2023 pool but mathematically drop it in 2024.
            # If the Retired Year is NaN, the plant is still actively operating.
            not_retired = df['Retired Year'].isna() | (df['Retired Year'] >= year)
            
            # Filter the active fleet for this specific year
            active_fleet = df[started & not_retired]
            
            # Sum the capacity per country
            annual_capacity = active_fleet.groupby('Country')['Capacity (MW)'].sum().reset_index()
            annual_capacity['Year'] = year
            annual_capacity['Technology'] = tech
            
            all_results.append(annual_capacity)
            
    # Combine all technologies and years into a single dataframe
    master_df = pd.concat(all_results, ignore_index=True)
    
    # Pivot the data so each technology gets its own column, filling missing techs with 0.0
    final_df = master_df.pivot_table(
        index=['Country', 'Year'], 
        columns='Technology', 
        values='Capacity (MW)', 
        fill_value=0.0
    ).reset_index()
    
    output_name = 'GEM_Estimated_Capacities_2023_2025.csv'
    final_df.to_csv(output_name, index=False)
    print(f"\n✓ Success! Master fallback file saved to '{output_name}'")

if __name__ == "__main__":
    generate_capacity_estimates()