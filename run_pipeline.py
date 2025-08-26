import subprocess
import sys
import os

scripts_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join("..", "dashboard", "dashboard.py")

scripts = [
    "collect_artifacts.py",
    "preprocess.py",
    "anomoly_detector.py",
    "rank_artifacts.py",
    "virustotal_checker.py",
    "abuselpdb_checker.py",
    "email_alert.py"
]

print("🚀 Starting full cyber triage pipeline...\n")

for script in scripts:
    print(f"\n▶ Running: {script}")
    result = subprocess.run(["python", script])
    if result.returncode != 0:
        print(f"❌ Error occurred in {script}. Aborting pipeline.")
        sys.exit(1)

# Launch dashboard in background
print("\n📊 Launching Streamlit dashboard...")
dashboard_proc = subprocess.Popen(["streamlit", "run", "dashboard.py"])

input("\n🔚 Press ENTER after reviewing the dashboard to continue...\n")
dashboard_proc.terminate()



print("\n🎉 All steps completed.")
