import pandas as pd

df = pd.read_csv("processed_data/scored_processes.csv")

df['risk_score'] = df['cpu_percent'].apply(lambda x: 3 if x > 90 else (2 if x > 50 else 1))
df.to_csv("processed_data/final_scored.csv", index=False)
print("✅ Risk Scoring Complete.")
