import requests
import os


def send_slack_alert(alert) -> bool:
    webhook = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("[Slack] No webhook configured")
        return False

    severity_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "🔶",
        "low": "🔵"
    }

    emoji = severity_emoji.get(alert.severity.lower(), "⚠️")
    source_label = "⚡ Wazuh SIEM" if alert.source == "wazuh" else "🤖 ML Model"

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} ThreatLens Alert — {alert.severity.upper()}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Attack Type:*\n{alert.attack_type.replace('_', ' ').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Amount:*\n₹{alert.amount:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Fraud Score:*\n{alert.fraud_score:.4f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*MITRE Tag:*\n{alert.mitre_tag or 'N/A'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Source:*\n{source_label}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Account:*\n{alert.account_id or 'N/A'}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Alert ID: `{alert.id}` | ThreatLens SOC Platform"
                    }
                ]
            }
        ]
    }

    try:
        r = requests.post(webhook, json=payload, timeout=5)
        print("[Slack] Status:", r.status_code)
        return r.status_code == 200
    except Exception as e:
        print("[Slack] Error:", e)
        return False