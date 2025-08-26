import requests
import psutil
import time
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY") 

def check_ip(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {
        "ipAddress": ip,
        "maxAgeInDays": "90"
    }
    headers = {
        "Accept": "application/json",
        "Key": API_KEY
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def extract_remote_ips():
    connections = psutil.net_connections()
    ip_set = set()
    for conn in connections:
        if conn.raddr:
            ip_set.add(conn.raddr.ip)
    return list(ip_set)

if __name__ == "__main__":
    ip_list = extract_remote_ips()
    print(f"\n🔍 Found {len(ip_list)} unique remote IPs. Checking AbuseIPDB...\n")

    for ip in ip_list:
        try:
            result = check_ip(ip)
            score = result["data"]["abuseConfidenceScore"]
            total_reports = result["data"]["totalReports"]
            if score >= 50:
                print(f"⚠  MALICIOUS: {ip} → Score: {score}, Reports: {total_reports}")
            else:
                print(f"✅ Clean: {ip} → Score: {score}")
            time.sleep(1.5)
        except Exception as e:
            print(f"❌ Error checking {ip}: {e}")
