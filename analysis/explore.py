import pandas as pd
from pathlib import Path

# Get the path of records.json
file_path = Path(__file__).resolve().parents[1] / "data" / "records.json"

# Load fort records into a DataFrame
df = pd.read_json(file_path)

print("\n===== GADKILLE DATA ANALYSIS =====")

# Fact 1: Total forts
print("\n1. Total forts:", len(df))

# Fact 2: Forts in each district
print("\n2. Forts by district:")
print(df["district"].value_counts())

# Fact 3: Missing information
print("\n3. Missing values:")
print(df[["height_ft", "base_village", "trek_notes"]].isnull().sum())