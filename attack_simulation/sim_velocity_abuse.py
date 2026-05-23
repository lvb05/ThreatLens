#!/usr/bin/env python3
"""
Velocity Abuse Attack Simulation
Simulates rapid burst of transactions from same account
Triggers Wazuh rule 100004 (T1110)
"""
import requests
import time
import random

API = "http://127.0.0.1:8000/api/v1/alerts"
ACCOUNT = f"ACC{random.randint(1000,9999)}"

print(f"[*] Starting Velocity Abuse simulation on account {ACCOUNT}...")
print("[*] Sending 8 rapid transactions in 30 seconds...")

for i in range(8):
    alert = {
        "amount": round(random.uniform(100, 800), 2),
        "fraud_score": round(random.uniform(0.70, 0.92), 4),
        "attack_type": "velocity_abuse",
        "severity": "high",
        "mitre_tag": "T1110",
        "source": "attack_simulation",
        "account_id": ACCOUNT,
        "ip_address": "45.142.212.100"
    }
    r = requests.post(API, json=alert)
    print(f"  [{i+1}/8] ₹{alert['amount']} from {ACCOUNT} → {r.status_code}")
    time.sleep(3)

print("[*] Velocity Abuse simulation complete.")