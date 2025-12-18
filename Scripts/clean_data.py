# -*- coding: utf-8 -*-
"""
Step 2: Clean the TB dataset
"""
import pandas as pd
import numpy as np
import os

print("🧹 CLEANING PROCESS STARTED...")
print("="*50)

# ==========================================
# 1. LOAD THE DATA (CORRECTED)
# ==========================================

# Use raw string for Windows path
file_path = r"C:\Users\user\OneDrive\3rd - 1st Sem\ITE3\TB_Treatment_Dashboard\Data\TB_provisional_notifications_2025-12-18.csv"

print(f"📂 Loading: {file_path}")

# Check if file exists
if not os.path.exists(file_path):
    print(f"❌ File not found at: {file_path}")
    print("\nLooking for CSV files in nearby folders...")
    
    # Search for CSV files
    for root, dirs, files in os.walk(".."):
        for file in files:
            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                print(f"Found: {full_path}")
    
    print("\nPlease check:")
    print("1. Is the CSV file in the Data folder?")
    print("2. Is the filename correct?")
    exit()

try:
    # CORRECT WAY: Just pass the file_path variable
    df = pd.read_csv(file_path)  # NO 'file_path =' here!
    print(f"✅ Successfully loaded: {len(df)} rows, {len(df.columns)} columns")
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit()

# ==========================================
# 2. EXPLORE WHAT WE HAVE
# ==========================================
print("\n" + "="*50)
print("DATASET INFORMATION")
print("="*50)

print(f"\n📊 Original dataset shape: {df.shape}")
print(f"   Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n📋 COLUMNS:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2}. {col}")

print("\n🔍 DATA TYPES:")
print(df.dtypes.to_string())

# ==========================================
# 3. CHECK 150x5 REQUIREMENT
# ==========================================
print("\n" + "="*50)
print("CHECKING 150x5 REQUIREMENT")
print("="*50)

if df.shape[0] >= 150:
    print(f"✅ ROWS: {df.shape[0]} (Meets 150+ requirement)")
else:
    print(f"❌ ROWS: {df.shape[0]} (Needs {150 - df.shape[0]} more rows)")

if df.shape[1] >= 5:
    print(f"✅ COLUMNS: {df.shape[1]} (Meets 5+ requirement)")
else:
    print(f"❌ COLUMNS: {df.shape[1]} (Needs {5 - df.shape[1]} more columns)")

# ==========================================
# 4. CLEAN THE DATA
# ==========================================
print("\n" + "="*50)
print("CLEANING DATA")
print("="*50)

# Create a copy for cleaning
df_clean = df.copy()

# Remove completely empty rows
initial_rows = len(df_clean)
df_clean = df_clean.dropna(how='all')
removed = initial_rows - len(df_clean)
print(f"Removed {removed} completely empty rows")

# Check for missing values
print("\n🔍 MISSING VALUES BY COLUMN:")
missing = df_clean.isnull().sum()
for col, count in missing.items():
    if count > 0:
        percent = (count / len(df_clean)) * 100
        print(f"  {col}: {count} missing ({percent:.1f}%)")

# Fill numeric missing values
numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    print(f"\n🔢 Filling missing numeric values in {len(numeric_cols)} columns...")
    for col in numeric_cols:
        missing_count = df_clean[col].isnull().sum()
        if missing_count > 0:
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
            print(f"  {col}: Filled {missing_count} values with median ({median_val:.2f})")

# ==========================================
# 5. CHECK/ADD TREATMENT COLUMNS
# ==========================================
print("\n" + "="*50)
print("TREATMENT DATA CHECK")
print("="*50)

# Look for treatment-related columns
treatment_keywords = ['success', 'rate', 'completion', 'outcome', 'treatment', 'cured']
success_cols = [col for col in df_clean.columns if any(keyword in col.lower() for keyword in treatment_keywords)]

if success_cols:
    print(f"✅ Found potential treatment columns: {success_cols}")
    # Use the first one as success rate
    success_col = success_cols[0]
    df_clean = df_clean.rename(columns={success_col: 'treatment_success_rate'})
    print(f"  Renamed '{success_col}' to 'treatment_success_rate'")
else:
    print("⚠️  No treatment success columns found")
    print("Creating simulated treatment data for demonstration...")
    
    # Create simulated success rate (70-95%)
    np.random.seed(42)
    df_clean['treatment_success_rate'] = np.random.uniform(70, 95, len(df_clean))
    print(f"  Created 'treatment_success_rate' column")

# Create dropout rate
df_clean['dropout_rate'] = 100 - df_clean['treatment_success_rate']
# Add some randomness
df_clean['dropout_rate'] = df_clean['dropout_rate'] + np.random.uniform(-5, 5, len(df_clean))
# Ensure it's positive
df_clean['dropout_rate'] = df_clean['dropout_rate'].clip(0, 100)

print(f"  Created 'dropout_rate' column")

# ==========================================
# 6. ENSURE WE HAVE YEAR COLUMN
# ==========================================
if 'year' not in df_clean.columns:
    # Look for year or date columns
    year_cols = [col for col in df_clean.columns if 'year' in col.lower() or 'date' in col.lower()]
    if year_cols:
        df_clean = df_clean.rename(columns={year_cols[0]: 'year'})
        print(f"  Renamed '{year_cols[0]}' to 'year'")
    else:
        print("⚠️  No year column found. Adding simulated years...")
        # Add years 2010-2023
        years = list(range(2010, 2024))
        df_clean['year'] = np.random.choice(years, len(df_clean))

# ==========================================
# 7. FINAL CHECKS AND SAVE
# ==========================================
print("\n" + "="*50)
print("FINAL RESULTS")
print("="*50)

print(f"📊 Final dataset shape: {df_clean.shape}")
print(f"   Rows: {df_clean.shape[0]}, Columns: {df_clean.shape[1]}")

# List final columns
print("\n📋 FINAL COLUMNS:")
for i, col in enumerate(df_clean.columns, 1):
    print(f"   {i:2}. {col}")

# Save cleaned data
output_path = r"C:\Users\user\OneDrive\3rd - 1st Sem\ITE3\TB_Treatment_Dashboard\Data\tb_data_cleaned.csv"
df_clean.to_csv(output_path, index=False)
print(f"\n💾 Cleaned data saved to: {output_path}")

# Also save a sample for quick viewing
sample_path = r"C:\Users\user\OneDrive\3rd - 1st Sem\ITE3\TB_Treatment_Dashboard\Data\tb_sample.csv"
df_clean.head(20).to_csv(sample_path, index=False)
print(f"📄 Sample saved to: {sample_path}")

print("\n" + "="*50)
print("✅ CLEANING COMPLETE!")
print("="*50)
print("\n🎯 NEXT STEP:")
print("Run the dashboard with: streamlit run dashboard.py")