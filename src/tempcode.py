from pathlib import Path
import pandas as pd

# 1. Setup path using forward slashes (avoids the syntax warnings)
file_path = Path("../data/sample.csv")

# 2. Load the data
print("--- STEP 1: Loading Data ---")
df = pd.read_csv(file_path)
print(f"Type BEFORE fix: {type(df['date'].iloc[0])}")

# 3. Convert AND re-assign to the column (CRITICAL STEP)
print("\n--- STEP 2: Converting Dates ---")
# errors='coerce' turns bad dates into NaT instead of crashing
df["date"] = pd.to_datetime(df["date"], errors="coerce") 

# 4. Save the changes back to the CSV
print("\n--- STEP 3: Saving File ---")
df.to_csv(file_path, index=False)
print("File saved successfully!")

# 5. Reload the file fresh from the disk to absolutely prove it worked
print("\n--- STEP 4: Verification ---")
df_verify = pd.read_csv(file_path)
print(f"Type AFTER reloading: {df_verify['date'].dtype}")