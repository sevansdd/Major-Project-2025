import json
import pandas as pd
import os

os.makedirs("processed_data", exist_ok=True)

with open("artifacts/processes.json") as f:
    proc_data = json.load(f)

df = pd.DataFrame(proc_data)
df.fillna("unknown", inplace=True)
df.to_csv("processed_data/processes.csv", index=False)
print("✅ Processed Data Saved.")
