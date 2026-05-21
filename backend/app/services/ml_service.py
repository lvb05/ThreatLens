import pickle
import numpy as np
import json
from pathlib import Path

ML_DIR = Path(__file__).parent.parent.parent.parent / "ml"

class MLService:
    def __init__(self):
        print("[ML] Loading model and SHAP explainer...")
        with open(ML_DIR / "fraud_model.pkl", "rb") as f:
            self.model = pickle.load(f)
        with open(ML_DIR / "shap_explainer.pkl", "rb") as f:
            self.explainer = pickle.load(f)
        with open(ML_DIR / "feature_names.pkl", "rb") as f:
            self.feature_names = pickle.load(f)
        print(f"[ML] Ready. Features: {len(self.feature_names)}")

    def predict(self, features: list) -> float:
        """Returns fraud probability score 0-1"""
        X = np.array(features).reshape(1, -1)
        return float(self.model.predict_proba(X)[0][1])

    def explain(self, features: list) -> str:
        """Returns top 3 SHAP features as JSON string"""
        X = np.array(features).reshape(1, -1)
        shap_values = self.explainer.shap_values(X)

        # Handle both old and new SHAP output formats
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # fraud class
        else:
            sv = shap_values[0]

        # Get top 3 by absolute importance
        importance = [(self.feature_names[i], float(sv[i]))
                      for i in range(len(self.feature_names))]
        top3 = sorted(importance, key=lambda x: abs(x[1]), reverse=True)[:3]

        result = [
            {"feature": f, "shap_value": round(v, 4),
             "direction": "fraud" if v > 0 else "normal"}
            for f, v in top3
        ]
        return json.dumps(result)

    def classify_attack(self, amount: float, fraud_score: float,
                        hour: int = 12) -> tuple[str, str, str]:
        """Returns (attack_type, severity, mitre_tag)"""
        if amount < 10 and fraud_score > 0.7:
            return "card_testing", "high", "T1133"
        elif fraud_score > 0.9 and amount > 50000:
            return "large_fraud", "critical", "T1657"
        elif fraud_score > 0.85 and 5000 < amount < 50000:
            return "account_takeover", "critical", "T1078"
        elif amount < 500 and fraud_score > 0.65:
            return "bot_attack", "medium", "T1059"
        else:
            return "velocity_abuse", "high", "T1110"

ml_service = MLService()