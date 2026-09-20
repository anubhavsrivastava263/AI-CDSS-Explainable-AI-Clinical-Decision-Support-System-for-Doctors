"""
XGBoost 30-Day Hospital Readmission Model Training Pipeline (Week 1 Baseline)
"""

import os
import json
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib

from download_or_generate_dataset import fetch_or_create_dataset
from preprocess import preprocess_data

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def train_readmission_model():
    print("=" * 60)
    print("AI-CDSS: Training XGBoost 30-Day Readmission Model (Week 1)")
    print("=" * 60)
    
    # 1. Fetch or generate raw dataset
    df = fetch_or_create_dataset()
    
    # 2. Preprocess dataset
    X_train, X_test, y_train, y_test, feature_names = preprocess_data(df)
    
    # 3. Calculate class balance weight for scale_pos_weight
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / max(pos_count, 1)
    print(f"[Training] Class Balance -> Non-Readmitted (0): {neg_count}, 30-Day Readmitted (1): {pos_count}")
    print(f"[Training] Computed scale_pos_weight: {scale_pos_weight:.2f}")
    
    # 4. Instantiate & Train XGBoost Classifier
    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss"
    )
    
    print("[Training] Fitting XGBoost Classifier...")
    model.fit(X_train, y_train)
    
    # 5. Evaluate on Test Split
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    try:
        roc_auc = float(roc_auc_score(y_test, y_prob))
    except Exception:
        roc_auc = 0.5
        
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # 6. Feature Importances
    importances = model.feature_importances_
    top_indices = np.argsort(importances)[::-1][:10]
    top_features = [
        {"feature": feature_names[i], "importance": float(importances[i])}
        for i in top_indices
    ]
    
    metrics = {
        "model_name": "XGBoost 30-Day Readmission Classifier (Week 1 Baseline)",
        "dataset": "UCI Diabetes 130-US Hospitals",
        "total_samples": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "num_features": len(feature_names),
        "evaluation_metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4)
        },
        "confusion_matrix": cm,
        "top_10_features": top_features
    }
    
    # 7. Save Model & Metrics
    model_path = os.path.join(MODELS_DIR, "xgboost_readmission.joblib")
    metrics_path = os.path.join(OUTPUTS_DIR, "metrics.json")
    
    joblib.dump(model, model_path)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("\n" + "=" * 60)
    print("TRAINING & EVALUATION SUMMARY:")
    print(f"  • Model saved to: {model_path}")
    print(f"  • Metrics saved to: {metrics_path}")
    print(f"  • ROC-AUC Score:  {metrics['evaluation_metrics']['roc_auc']}")
    print(f"  • Accuracy:       {metrics['evaluation_metrics']['accuracy']}")
    print(f"  • Recall:         {metrics['evaluation_metrics']['recall']}")
    print(f"  • F1-Score:       {metrics['evaluation_metrics']['f1_score']}")
    print("\nTop Most Influential Features:")
    for tf in top_features[:5]:
        print(f"    - {tf['feature']}: {tf['importance']:.4f}")
    print("=" * 60)
    
    return metrics

if __name__ == "__main__":
    train_readmission_model()
