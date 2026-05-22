import json
import time
import requests

ALERT_FILE = "/var/ossec/logs/alerts/alerts.json"
THREATLENS_API = "http://192.168.56.1:8000/api/v1/alerts"

seen = set()


def tail_alerts():
    with open(ALERT_FILE, "r") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()

            if not line:
                time.sleep(2)
                continue

            try:
                alert = json.loads(line)
                yield alert
            except Exception:
                continue


for alert in tail_alerts():
    try:
        rule = alert.get("rule", {})
        description = rule.get("description", "")
        alert_id = alert.get("id")

        # only forward fraud-related alerts
        if "transaction" not in description.lower() and "fraud" not in description.lower():
            continue

        if not alert_id:
            continue

        if alert_id in seen:
            continue

        payload = {
            "amount": 75000,
            "fraud_score": 0.95,
            "attack_type": description,
            "severity": "high",
            "mitre_tag": (
                rule.get("mitre", {}).get("id", ["unknown"])[0]
                if rule.get("mitre")
                else "unknown"
            ),
            "source": "wazuh",
            "ip_address": alert.get("agent", {}).get("ip", "127.0.0.1"),
            "account_id": alert.get("agent", {}).get("name", "ubuntu"),
            "shap_json": "{}"
        }

        resp = requests.post(THREATLENS_API, json=payload)

        print("POST:", resp.status_code)
        print("Forwarded:", payload)

        seen.add(alert_id)

    except Exception as e:
        print("Error:", e)