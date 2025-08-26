import requests
import hashlib
import os
import json
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_virustotal(file_hash):
    headers = {"x-apikey": API_KEY}
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        stats = result["data"]["attributes"]["last_analysis_stats"]
        return stats
    else:
        return {"error": f"Status {response.status_code}: {response.text}"}

def scan_executables(start_dirs, max_files=10):
    scanned = 0
    for root_dir in start_dirs:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    try:
                        print(f"\n🔍 Scanning: {full_path}")
                        file_hash = get_file_hash(full_path)
                        result = check_virustotal(file_hash)
                        
                        if isinstance(result, dict) and 'malicious' in result:
                            detections = result['malicious'] + result.get('suspicious', 0)
                            if detections > 0:
                                print(f"⚠ RISKY FILE DETECTED: {file} — Malicious: {result['malicious']}, Suspicious: {result['suspicious']}")
                                print(json.dumps(result, indent=2))
                            else:
                                print("✅ Clean.")
                        else:
                            print("❌ Error from VirusTotal:", result)

                        scanned += 1
                        if scanned >= max_files:
                            return
                    except Exception as e:
                        print(f"❌ Error processing {file}: {e}")
                        continue

if __name__ == "__main__":
    # Directories to scan
    directories_to_scan = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser(r"~\AppData\Local"),
        os.path.expanduser(r"~\Downloads")
    ]

    print("🚀 Auto-scanning for suspicious .exe files...")
    scan_executables(directories_to_scan, max_files=5)  # Limit for quick tests