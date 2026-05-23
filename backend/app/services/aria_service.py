import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    _groq_available = True
except ImportError:
    _groq_available = False


def get_client():
    if not _groq_available:
        raise Exception("groq package not installed")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not found")
    return Groq(api_key=api_key)


def analyze_alert(alert):
    try:
        client = get_client()
        shap_text = "No SHAP explanation available."
        if alert.shap_json:
            try:
                shap_data = json.loads(alert.shap_json)
                shap_lines = []
                for item in shap_data:
                    shap_lines.append(
                        f"{item['feature']}: {item['shap_value']} ({item['direction']})"
                    )
                shap_text = "\n".join(shap_lines)
            except Exception:
                pass

        prompt = f"""
You are ARIA, an expert SOC AI analyst inside ThreatLens.
Analyze this fraud/security alert.
Attack Type: {alert.attack_type}
Amount: ₹{alert.amount}
Fraud Score: {alert.fraud_score}
Severity: {alert.severity}
MITRE Technique: {alert.mitre_tag}
Source: {alert.source}
IP Address: {alert.ip_address}
Account ID: {alert.account_id}
SHAP explanation:
{shap_text}
Return:
1. Executive Summary
2. Why It Was Flagged
3. MITRE Explanation
4. Risk Assessment
5. Recommended Response Actions
Be concise and professional.
"""
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert cybersecurity SOC analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=700
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ARIA analysis failed: {str(e)}"
