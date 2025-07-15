import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("processed_data/processes.csv")

features = df[['cpu_percent']].fillna(0)

model = IsolationForest(contamination=0.1)
df['anomaly'] = model.fit_predict(features)
df['risk'] = df['anomaly'].map({-1: "Suspicious", 1: "Normal"})
df.to_csv("processed_data/scored_processes.csv", index=False)
print("✅ Anomaly Detection Done.")
