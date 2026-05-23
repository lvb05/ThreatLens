# ThreatLens Detection Validation Report

## 1. Card Testing Detection

ThreatLens successfully detected simulated card testing behavior involving repeated low-value fraudulent transactions.

Validation results:
- Attack Type: Card Testing
- MITRE ATT&CK Mapping: T1133
- High severity alert generated
- Fraud score exceeded 0.98
- SHAP explainability visualization generated
- Alert displayed in live dashboard
- ARIA AI analysis available
- PDF incident export available

Evidence:
- screenshots/card_testing.png

---

## 2. Threat Intelligence Enrichment (AbuseIPDB)

ThreatLens enriched suspicious source IPs using AbuseIPDB threat intelligence.

Validation results:
- IP reputation lookup successful
- Abuse confidence score retrieved
- Country resolved
- ISP metadata resolved
- Threat intelligence displayed directly in dashboard alert details

Example:
- Abuse Score: 59
- Country: LT
- ISP: Flyservers S.A.

Evidence:
- screenshots/velocity_abuse.png

---

## 3. SOC Alerting via Slack

ThreatLens successfully pushed high-severity alerts to Slack in real time.

Validation results:
- Incoming webhook integration functional
- High severity alerts delivered instantly
- Alert metadata included:
  - Attack type
  - Fraud score
  - MITRE tag
  - Account ID
  - Alert ID
  - Source

Evidence:
- screenshots/slack_alert.png

---

## Validation Summary

ThreatLens successfully demonstrated:

- Real-time ML fraud detection
- SHAP explainability
- MITRE ATT&CK attack mapping
- ARIA AI analyst investigation
- PDF incident reporting
- Slack SOC alerting
- AbuseIPDB threat intelligence enrichment
- Live SOC dashboard monitoring
