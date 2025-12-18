# -*- coding: utf-8 -*-
"""
Step 1: Explore the TB dataset
"""
import pandas as pd
import os

# ==========================================
# FIXED: Use raw string or forward slashes
# ==========================================

# OPTION 1: Use raw string (add 'r' before the string)
file_path = r"C:\Users\user\OneDrive\3rd - 1st Sem\ITE3\TB_Treatment_Dashboard\Data\TB_provisional_notifications_2025-12-18.csv"

# OR OPTION 2: Use forward slashes (works on Windows too)
# file_path = "C:/Users/user/OneDrive/3rd - 1st Sem/ITE3/TB_Treatment_Dashboard/Data/TB_provisional_notifications_2025-12-18.csv"

# OR OPTION 3: Use double backslashes
# file_path = "C:\\Users\\user\\OneDrive\\3rd - 1st Sem\\ITE3\\TB_Treatment_Dashboard\\Data\\TB_provisional_notifications_2025-12-18.csv"

print(f"Looking for file at: {file_path}")

# Check if file exists
if os.path.exists(file_path):
    print("✅ File found!")
    try:
        df = pd.read_csv(file_path)
        print("✅ File loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        exit()
else:
    print("❌ File not found!")
    print("Current working directory:", os.getcwd())
    
    # Try to find the file
    print("\nSearching for CSV files...")
    for root, dirs, files in os.walk(".."):
        for file in files:
            if file.endswith(".csv"):
                print(f"Found: {os.path.join(root, file)}")
    exit()

print("="*50)
print("DATASET EXPLORATION")
print("="*50)

# 1. Basic info
print("\n1. SHAPE OF DATA:")
print(f"   Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n2. COLUMN NAMES:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")

print("\n3. FIRST 5 ROWS:")
print(df.head())

print("\n4. DATA TYPES:")
print(df.dtypes)

print("\n5. CHECK FOR MISSING VALUES:")
missing = df.isnull().sum()
print(missing[missing > 0])  # Show only columns with missing values

# Save this info to a text file
with open("../documentation/data_info.txt", "w") as f:
    f.write(f"Dataset Shape: {df.shape}\n")
    f.write(f"Columns: {list(df.columns)}\n")
    f.write(f"Missing Values:\n{df.isnull().sum()}\n")

print("\n✅ Data exploration complete!")
print("Report saved to: ../documentation/data_info.txt")