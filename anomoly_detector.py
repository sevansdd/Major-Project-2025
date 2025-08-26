import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import sys # Importing sys to provide a cleaner exit from the script

# --- Step 0: Initial Setup and Data Loading ---
try:
    # Attempt to load the dataset
    df = pd.read_csv("processed_data/processes.csv")
    print("✅ Successfully loaded 'processed_data/processes.csv'.")
except FileNotFoundError:
    # Handle the case where the file is not found
    print("❌ Error: The file 'processed_data/processes.csv' was not found.")
    print("Please ensure the folder 'processed_data' exists and contains the 'processes.csv' file.")
    sys.exit(1) # Exit the script with an error code

# Ensure the 'cpu_percent' column exists and handle missing values
if 'cpu_percent' not in df.columns:
    print("❌ Error: The DataFrame does not contain a 'cpu_percent' column.")
    print("Please check the column names in your CSV file.")
    sys.exit(1)

# Fill any missing values with 0 for the anomaly detection models
features = df[['cpu_percent']].fillna(0)
print("✅ Data prepared for anomaly detection.")

# --- Step 1: Anomaly Detection with Isolation Forest ---
print("\nStep 1: Running Isolation Forest...")
model_if = IsolationForest(contamination=0.1, random_state=42)
df['anomaly_if'] = model_if.fit_predict(features)
df['risk_if'] = df['anomaly_if'].map({-1: "Suspicious", 1: "Normal"})
print("✅ Isolation Forest completed. Initial risk scores assigned.")

# --- Step 2: Refine 'Suspicious' data points with LOF ---
suspicious_indices = df[df['risk_if'] == 'Suspicious'].index

if not suspicious_indices.empty:
    print(f"\nStep 2: Found {len(suspicious_indices)} suspicious data points. Running Local Outlier Factor (LOF)...")
    
    # Isolate the features of the suspicious data points.
    suspicious_features = df.loc[suspicious_indices, ['cpu_percent']]
    
    # Initialize and fit the LOF model
    model_lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
    lof_scores = model_lof.fit_predict(suspicious_features)
    
    # Map the LOF scores to human-readable risk levels.
    # We use a temporary column to avoid any pandas warnings.
    df.loc[suspicious_indices, 'final_risk_temp'] = pd.Series(lof_scores, index=suspicious_indices).map({
        -1: "Highly Suspicious",
        1: "Suspicious (Confirmed by IF)"
    })
    
    # Create the final 'risk' column by filling in the normal rows.
    df['final_risk'] = df['final_risk_temp'].fillna(df['risk_if'])
    
    # Clean up the temporary column
    df.drop('final_risk_temp', axis=1, inplace=True)
    
    print("✅ LOF analysis completed. Risk scores refined.")
else:
    print("\nNo suspicious data points found by Isolation Forest. Skipping LOF analysis.")
    # If no suspicious data is found, the final risk is the same as the initial one.
    df['final_risk'] = df['risk_if']

# --- Step 3: Save the Final Results ---
output_path = "processed_data/scored_processes_integrated_lof.csv"
try:
    df.to_csv(output_path, index=False)
    print(f"\n✅ All analysis completed. Final results saved to '{output_path}'.")
except Exception as e:
    print(f"❌ Error: Could not save the file to '{output_path}'. Reason: {e}")
    sys.exit(1)