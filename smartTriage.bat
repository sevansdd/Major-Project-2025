@echo off
echo 🚀 Starting Smart Triage Setup on Windows...

:: Step 1: Set up virtual environment
if not exist venv (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

:: Step 2: Activate environment
call venv\Scripts\activate

:: Step 3: Install requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt

:: Step 4: Run pipeline
echo 🧠 Running full triage pipeline...
python live_monitor.py

:: Step 5: Launch Streamlit dashboard
echo 🌐 Launching dashboard...
start "" http://localhost:8501
streamlit run dashboard.py --server.headless false --browser.serverAddress=127.0.0.1

pause