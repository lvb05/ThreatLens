import os
import requests


def lookup_ip(ip: str):
    api_key = os.getenv("ABUSEIPDB_KEY", "")
    if not api_key or not ip:
        return None

    try:
        r = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={
                "Key": api_key,
                "Accept": "application/json"
            },
            params={
                "ipAddress": ip,
                "maxAgeInDays": 90
            },
            timeout=5
        )

        if r.status_code != 200:
            print("[AbuseIPDB] Error:", r.text)
            return None

        data = r.json()["data"]

        return {
            "abuse_score": data.get("abuseConfidenceScore", 0),
            "country": data.get("countryCode", "Unknown"),
            "isp": data.get("isp", "Unknown")
        }

    except Exception as e:
        print("[AbuseIPDB] Exception:", e)
        return None