#!/usr/bin/env python3
"""
Full Purple Team Test — runs all attack simulations in sequence
Use this to verify all Wazuh rules fire correctly
"""
import subprocess
import sys
import time

scripts = [
    ("Card Testing (T1133)",    "sim_card_testing.py"),
    ("Velocity Abuse (T1110)",  "sim_velocity_abuse.py"),
    ("Large Fraud (T1657)",     "sim_large_fraud.py"),
]

print("=" * 50)
print("  ThreatLens — Full Purple Team Simulation")
print("=" * 50)

for name, script in scripts:
    print(f"\n[>>] Running: {name}")
    subprocess.run([sys.executable, script])
    print(f"[<<] Done: {name}")
    time.sleep(5)

print("\n[*] All simulations complete.")
print("[*] Check ThreatLens dashboard — should see all attack types")
print("[*] Check Wazuh Security Events — rules should have fired")