import requests
import hashlib
import json
import os

API_KEY = '13c98fc7117c544ddeec26899f6d983cbcd6b2a92a48daf12fe8350251297d23'  # Replace with your VirusTotal API key

def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_virustotal(file_hash):
    headers = {"x-apikey": API_KEY}
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result["data"]["attributes"]["last_analysis_stats"]
    else:
        return {"error": f"Status {response.status_code}: {response.text}"}

if __name__ == "__main__":
    test_file = "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"  # Replace with actual file path
    hash_val = get_file_hash(test_file)
    result = check_virustotal(hash_val)
    print(json.dumps(result, indent=2))
