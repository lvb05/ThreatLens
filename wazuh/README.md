# ThreatLens – Wazuh SIEM Integration

## Architecture
Fraud logs → Wazuh Manager → bridge.py → FastAPI Backend → React Dashboard

## Components
- fraud_generator.py → generates synthetic UPI transaction logs
- fraud_rules.xml → custom Wazuh fraud detection rules
- bridge.py → forwards Wazuh alerts to backend API

## Detection Rules
- Rule 100001: UPI transaction baseline log
- Rule 100002: Suspicious transaction detection
- Rule 100003: Large fraud detection

## Ubuntu Setup
- Wazuh Manager installed on Ubuntu VM
- Custom rules path: `/var/ossec/etc/rules/fraud_rules.xml`
- Alert file: `/var/ossec/logs/alerts/alerts.json`

## Run
```bash
python3 ~/fraud_generator.py
python3 ~/bridge.py
sudo systemctl status wazuh-manager
```