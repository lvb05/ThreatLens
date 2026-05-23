#!/usr/bin/env python3
"""
Card Testing Attack Simulation
Simulates rapid micro-transactions to test stolen card validity
Triggers Wazuh rule 100002 (T1133)
"""
import requests
import time
import random

API = "http://127.0.0.1:8000/api/v1/alerts"

print("[*] Starting Card Testing simulation...")
print("[*] Sending 10 micro-transactions (amount < ₹10)...")

for i in range(10):
    alert = {
        "amount": round(random.uniform(0.5, 9.99), 2),
        "fraud_score": round(random.uniform(0.75, 0.99), 4),
        "attack_type": "card_testing",
        "severity": "high",
        "mitre_tag": "T1133",
        "source": "attack_simulation",
        "account_id": f"ACC{random.randint(1000,9999)}",
        "ip_address": "185.220.101.5"
    }
    r = requests.post(API, json=alert)
    print(f"  [{i+1}/10] ₹{alert['amount']} → {r.status_code}")
    time.sleep(1.5)

print("[*] Card Testing simulation complete.")
print("[*] Check Wazuh dashboard → Security Events for rule 100002")
print("[*] Check ThreatLens dashboard for HIGH severity card_testing alerts")