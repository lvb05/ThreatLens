import asyncio
import random
import numpy as np
import pandas as pd
from pathlib import Path

FAKE_IPS = [
    "103.21.244.0", "185.220.101.5", "45.142.212.100",
    "194.165.16.11", "91.108.4.0", "198.54.117.200"
]

# Load real fraud rows from dataset at startup
ML_DIR = Path(__file__).parent.parent.parent.parent / "ml"
_fraud_df = None

def get_fraud_samples():
    global _fraud_df
    if _fraud_df is None:
        csv_path = ML_DIR / "creditcard.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            _fraud_df = df[df["Class"] == 1].drop("Class", axis=1)
            print(f"[Simulator] Loaded {len(_fraud_df)} real fraud samples")
        else:
            _fraud_df = pd.DataFrame()
    return _fraud_df

def generate_features(force_fraud=False):
    """Mix real fraud rows (70%) with gaussian noise (30%)"""
    fraud_df = get_fraud_samples()

    if force_fraud and len(fraud_df) > 0:
        # Use a real fraud row from the dataset
        row = fraud_df.sample(1).iloc[0]
        return list(row.values)
    else:
        # Gaussian noise — will mostly score low
        time = random.randint(0, 172800)
        v_features = [round(random.gauss(0, 1), 4) for _ in range(28)]
        amount = round(random.uniform(1, 5000), 2)
        return [time] + v_features + [amount]

async def run_simulator(manager, db_session_factory):
    from app.models.alert import Alert
    from app.services.ml_service import ml_service

    get_fraud_samples()  # preload
    print("[Simulator] Started — using real fraud samples from dataset...")
    await asyncio.sleep(3)

    call_count = 0
    while True:
        try:
            call_count += 1
            # Every other call use a real fraud row to guarantee alerts
            force_fraud = (call_count % 2 == 0)
            features = generate_features(force_fraud=force_fraud)
            fraud_score = ml_service.predict(features)
            amount = float(features[-1]) 

            if fraud_score > 0.5:
                attack_type, severity, mitre_tag = ml_service.classify_attack(
                    amount, fraud_score
                )
                shap_json = ml_service.explain(features)

                db = db_session_factory()
                try:
                    alert = Alert(
                        amount=round(amount, 2),
                        fraud_score=round(fraud_score, 4),
                        attack_type=attack_type,
                        severity=severity,
                        mitre_tag=mitre_tag,
                        source="ml_model",
                        ip_address=random.choice(FAKE_IPS),
                        account_id=f"ACC{random.randint(1000,9999)}",
                        shap_json=shap_json,
                        status="open"
                    )
                    db.add(alert)
                    db.commit()
                    db.refresh(alert)

                    await manager.broadcast({
                        "type": "new_alert",
                        "alert": {
                            "id": alert.id,
                            "timestamp": str(alert.timestamp),
                            "amount": alert.amount,
                            "fraud_score": alert.fraud_score,
                            "attack_type": alert.attack_type,
                            "severity": alert.severity,
                            "mitre_tag": alert.mitre_tag,
                            "source": alert.source,
                            "ip_address": alert.ip_address,
                            "account_id": alert.account_id,
                            "shap_json": alert.shap_json,
                            "status": alert.status
                        }
                    })
                    print(f"[Simulator] ✓ {attack_type} | "
                          f"₹{amount:.2f} | Score: {fraud_score:.4f} | SHAP ✓")
                finally:
                    db.close()
            else:
                print(f"[Simulator] Normal (score {fraud_score:.3f}) — skipped")

        except Exception as e:
            print(f"[Simulator] Error: {e}")

        await asyncio.sleep(random.uniform(8, 15))