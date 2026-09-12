import pandas as pd
import numpy as np
import re

def clean_and_process_data(file_path):
    # 1. Load Dataset
    df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
    print("Initial Data Shape:", df.shape)

    # Standardize column names (lowercase with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Map World Bank dataset columns to standardized names
    column_mapping = {
        'series_code': 'indicator_code',
        'series_name': 'indicator_name'
    }
    df = df.rename(columns=column_mapping)

    # 2. Identify year columns strictly by checking for 4 digits (e.g., '1970', '2022')
    id_vars = [c for c in ['country_name', 'country_code', 'indicator_name', 'indicator_code'] if c in df.columns]
    year_cols = [c for c in df.columns if re.match(r'^\d{4}$', str(c))]
    
    # Melt yearly columns into a single 'debt' column
    df = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='year', value_name='debt')

    # 3. Data Cleaning
    # Drop rows missing core identification attributes
    df = df.dropna(subset=['country_name', 'indicator_code'])

    # Format debt values to numeric and handle missing/zero values
    df['debt'] = pd.to_numeric(df['debt'], errors='coerce').fillna(0)

    # Deep clean text columns to remove padding and trailing spaces (e.g. 'AFG       ' -> 'AFG')
    for col in id_vars:
        df[col] = df[col].astype(str).str.strip()

    # Remove duplicates
    df = df.drop_duplicates()

    # 4. Save Cleaned File
    cleaned_file = "cleaned_international_debt.csv"
    df.to_csv(cleaned_file, index=False)
    print(f"Cleaned dataset shape: {df.shape}")
    print(f"Cleaned dataset saved successfully to {cleaned_file}")
    
    return df

if __name__ == "__main__":
    clean_and_process_data("IDS_ALLCountries_Data.csv")