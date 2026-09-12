import pandas as pd
from sqlalchemy import create_engine, text

# Database Connection Credentials (Update password if needed)
DB_USER = "root"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "international_debt_db"

# 1. Connect and create database
engine_server = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/")
with engine_server.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
    print(f"Database '{DB_NAME}' created or verified.")

# 2. Connect to specific database
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Load the newly cleaned data (Added low_memory=False to fix the DType warning)
print("Loading cleaned dataset...")
df = pd.read_csv("cleaned_international_debt.csv", low_memory=False)

# 3. Table Normalization
countries_df = df[['country_name', 'country_code']].drop_duplicates().reset_index(drop=True)
indicators_df = df[['indicator_name', 'indicator_code']].drop_duplicates().reset_index(drop=True)
debt_df = df[['country_code', 'indicator_code', 'year', 'debt']]

# 4. Safely Reset Schema & Insert Tables into MySQL
with engine.begin() as conn:
    # Fix for Foreign Key Error: Drop the child table BEFORE the parent tables
    conn.execute(text("DROP TABLE IF EXISTS international_debt;"))
    conn.execute(text("DROP TABLE IF EXISTS countries;"))
    conn.execute(text("DROP TABLE IF EXISTS indicators;"))
    
    # Create normalized schema explicitly
    conn.execute(text("""
    CREATE TABLE countries (
        country_code VARCHAR(10) PRIMARY KEY,
        country_name VARCHAR(255) NOT NULL
    );
    """))
    
    conn.execute(text("""
    CREATE TABLE indicators (
        indicator_code VARCHAR(255) PRIMARY KEY,
        indicator_name TEXT NOT NULL
    );
    """))

    conn.execute(text("""
    CREATE TABLE international_debt (
        id INT AUTO_INCREMENT PRIMARY KEY,
        country_code VARCHAR(10),
        indicator_code VARCHAR(255),
        year VARCHAR(10),
        debt DECIMAL(25, 2),
        FOREIGN KEY (country_code) REFERENCES countries(country_code),
        FOREIGN KEY (indicator_code) REFERENCES indicators(indicator_code)
    );
    """))

# 5. Upload Data in chunks (Changed to 'append' since we already dropped/created empty tables)
print("Uploading Countries...")
countries_df.to_sql('countries', con=engine, if_exists='append', index=False)

print("Uploading Indicators...")
indicators_df.to_sql('indicators', con=engine, if_exists='append', index=False)

print("Uploading Debt Data (This may take a few minutes)...")
debt_df.to_sql('international_debt', con=engine, if_exists='append', index=False, chunksize=15000)

print("Data successfully ingested into normalized MySQL tables.")