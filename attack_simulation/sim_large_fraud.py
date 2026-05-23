#!/usr/bin/env python3
"""
Large Fraud Attack Simulation
Simulates high-value fraudulent transactions
Triggers Wazuh rule 100003 (T1657)
"""
import requests
import random
import time

API = "http://127.0.0.1:8000/api/v1/alerts"

print("[*] Starting Large Fraud simulation...")
print("[*] Sending 5 high-value transactions (amount > ₹50000)...")

for i in range(5):
    amount = round(random.uniform(50000, 200000), 2)
    alert = {
        "amount": amount,
        "fraud_score": round(random.uniform(0.88, 0.99), 4),
        "attack_type": "large_fraud",
        "severity": "critical",
        "mitre_tag": "T1657",
        "source": "attack_simulation",
        "account_id": f"ACC{random.randint(1000,9999)}",
        "ip_address": "194.165.16.11"
    }
    r = requests.post(API, json=alert)
    print(f"  [{i+1}/5] ₹{amount:,.2f} → {r.status_code}")
    time.sleep(2)

print("[*] Large Fraud simulation complete.")