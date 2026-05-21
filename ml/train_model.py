import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, recall_score
from pathlib import Path

print("[1/5] Loading dataset...")
df = pd.read_csv(Path(__file__).parent / "creditcard.csv")
print(f"      {len(df):,} transactions, {df['Class'].sum()} fraud cases")

print("[2/5] Preparing features...")
X = df.drop("Class", axis=1)
y = df["Class"]

# Handle class imbalance — fraud is only 0.17% of data
scale_pos_weight = (y == 0).sum() / (y == 1).sum()
print(f"      Class imbalance ratio: {scale_pos_weight:.1f}x")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("[3/5] Training XGBoost model...")
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    use_label_encoder=False,
    eval_metric="aucpr",
    random_state=42,
    n_jobs=-1
)
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

print("[4/5] Evaluating model...")
y_pred = model.predict(X_test)
recall = recall_score(y_test, y_pred)
print(f"      Recall: {recall:.1%}")
print(classification_report(y_test, y_pred, target_names=["Normal", "Fraud"]))

print("[5/5] Saving model + SHAP explainer...")
output_dir = Path(__file__).parent
with open(output_dir / "fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

# Pre-build SHAP explainer and save it too
explainer = shap.TreeExplainer(model)
with open(output_dir / "shap_explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

# Save feature names for the API
feature_names = list(X.columns)
with open(output_dir / "feature_names.pkl", "wb") as f:
    pickle.dump(feature_names, f)

print(f"\n✅ Done! Files saved to {output_dir}")
print("   fraud_model.pkl")
print("   shap_explainer.pkl")
print("   feature_names.pkl")