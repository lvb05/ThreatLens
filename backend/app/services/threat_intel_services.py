import os
import requests


def enrich_ip(ip_address: str):
    api_key = os.getenv("ABUSEIPDB_KEY", "")

    if not api_key or not ip_address:
        return None

    try:
        headers = {
            "Key": api_key,
            "Accept": "application/json"
        }

        params = {
            "ipAddress": ip_address,
            "maxAgeInDays": 90
        }

        r = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers=headers,
            params=params,
            timeout=5
        )

        if r.status_code != 200:
            print("[AbuseIPDB] Error:", r.status_code)
            return None

        data = r.json()["data"]

        return {
            "abuse_score": data.get("abuseConfidenceScore", 0),
            "country": data.get("countryCode", "N/A"),
            "isp": data.get("isp", "Unknown")
        }

    except Exception as e:
        print("[AbuseIPDB] Error:", e)
        return None