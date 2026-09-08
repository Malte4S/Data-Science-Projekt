import os
import glob
import pandas as pd

INPUT_DIR = "Installed_Capacity_By_Country"
OUTPUT_DIR = "Final_Validated_Capacity"
GEM_FILE = "GEM_Estimated_Capacities_2023_2025.csv"
TARGET_TECHS = ['Bioenergy', 'Hydro', 'Wind', 'Solar']

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(GEM_FILE):
        print(f"[Error] Missing '{GEM_FILE}'.")
        return
        
    gem_df = pd.read_csv(GEM_FILE)
    files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    print("--- Starting Capacity Validation (EC vs GEM) ---")
    
    for file_path in files:
        filename = os.path.basename(file_path)
        country = filename.split('_')[0]
        
        cap_df = pd.read_csv(file_path)
        gem_country_df = gem_df[gem_df['Country'] == country]
        
        if not gem_country_df.empty:
            for year in [2023, 2024, 2025]:
                cap_mask = cap_df['Year'] == year
                gem_mask = gem_country_df['Year'] == year
                
                if cap_mask.any() and gem_mask.any():
                    for tech in TARGET_TECHS:
                        ec_val = cap_df.loc[cap_mask, tech].values[0]
                        gem_val = gem_country_df.loc[gem_mask, tech].values[0]
                        # Directly overwrite with whichever physical capacity is larger
                        cap_df.loc[cap_mask, tech] = max(ec_val, gem_val)
                        
        out_path = os.path.join(OUTPUT_DIR, filename)
        cap_df.to_csv(out_path, index=False)
        print(f"✓ Validated {country}")
        
    print(f"\nAll files saved to '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()