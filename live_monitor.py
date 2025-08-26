import psutil
import time
import subprocess
import datetime
import os
from abuselpdb_checker import extract_remote_ips, check_ip

THREAT_CPU_THRESHOLD = 90
THREAT_IP_SCORE_THRESHOLD = 70
CHECK_INTERVAL = 60  # seconds

LOG_FILE = "incident_logs.txt"
PIPELINE_SCRIPT = os.path.join(os.path.dirname(__file__), "run_pipeline.py")

def log_incident(details):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{datetime.datetime.now()} - {details}\n")

def check_high_cpu():
    print("Checking CPU usage...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=1)
            if cpu > THREAT_CPU_THRESHOLD:
                return f"High CPU usage detected: {proc.name()} ({cpu}%)"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def check_malicious_ips():
    print("Checking remote IPs...")
    try:
        ips = extract_remote_ips()
        print(f"Found IPs: {ips}")
        for ip in ips:
            try:
                result = check_ip(ip)
                score = result["data"]["abuseConfidenceScore"]
                if score >= THREAT_IP_SCORE_THRESHOLD:
                    return f"Malicious IP detected: {ip} (Abuse Score: {score})"
            except Exception:
                continue
    except Exception as e:
        print("IP check failed:", e)
    return None

def trigger_response(reason):
    print(f"\n🚨 Threat detected: {reason}")
    log_incident(f"Threat Detected -> {reason}")
    subprocess.run(["python", PIPELINE_SCRIPT])

def main():
    print("🔍 Live Monitoring Activated. Checking every 60 seconds...\n")
    psutil.cpu_percent(interval=None)  # Warm up
    while True:
        threat = check_high_cpu() or check_malicious_ips()
        if threat:
            trigger_response(threat)
        else:
            print(f"{datetime.datetime.now()} – System looks clean.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
