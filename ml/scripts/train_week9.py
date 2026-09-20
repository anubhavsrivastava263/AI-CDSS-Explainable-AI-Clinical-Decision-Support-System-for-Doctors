"""Week 9 model comparison, tuning, validation, and calibration report.

Run from this directory: python train_week9.py
Use --quick for a faster three-fold comparison on a reproducible sample.
"""
import argparse
import json
import os

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from xgboost import XGBClassifier

from download_or_generate_dataset import fetch_or_create_dataset
from preprocess import preprocess_data

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR, OUTPUTS_DIR = os.path.join(BASE_DIR, "models"), os.path.join(BASE_DIR, "outputs")


def scores(y_true, probabilities, threshold=0.5):
    predicted = (probabilities >= threshold).astype(int)
    return {"accuracy": round(float(accuracy_score(y_true, predicted)), 4), "precision": round(float(precision_score(y_true, predicted, zero_division=0)), 4), "recall": round(float(recall_score(y_true, predicted, zero_division=0)), 4), "f1_score": round(float(f1_score(y_true, predicted, zero_division=0)), 4), "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4), "confusion_matrix": confusion_matrix(y_true, predicted).tolist()}


def build_xgb(weight, params):
    return XGBClassifier(random_state=42, eval_metric="logloss", n_jobs=-1, scale_pos_weight=weight, **params)


def train_week9(quick=False):
    os.makedirs(MODELS_DIR, exist_ok=True); os.makedirs(OUTPUTS_DIR, exist_ok=True)
    df = fetch_or_create_dataset()
    X_train, X_test, y_train, y_test, feature_names = preprocess_data(df)
    if quick and len(X_train) > 30000:
        X_train, _, y_train, _ = train_test_split(
            X_train, y_train, train_size=30000, stratify=y_train, random_state=42
        )
    weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    candidates = {
        "baseline_xgboost": {"n_estimators": 150, "max_depth": 4, "learning_rate": .08, "subsample": .8, "colsample_bytree": .8},
        "tuned_shallow_xgboost": {"n_estimators": 260, "max_depth": 3, "learning_rate": .05, "min_child_weight": 4, "subsample": .85, "colsample_bytree": .85, "reg_lambda": 2},
        "tuned_balanced_xgboost": {"n_estimators": 220, "max_depth": 5, "learning_rate": .04, "min_child_weight": 6, "subsample": .8, "colsample_bytree": .75, "reg_lambda": 3},
    }
    comparison = {"logistic_regression": round(float(cross_val_score(LogisticRegression(max_iter=500, class_weight="balanced"), X_train, y_train, cv=folds, scoring="roc_auc", n_jobs=-1).mean()), 4)}
    for name, params in candidates.items(): comparison[name] = round(float(cross_val_score(build_xgb(weight, params), X_train, y_train, cv=folds, scoring="roc_auc", n_jobs=-1).mean()), 4)
    winner = max(candidates, key=lambda name: comparison[name])
    raw_model = build_xgb(weight, candidates[winner]).fit(X_train, y_train)
    raw_probability = raw_model.predict_proba(X_test)[:, 1]
    calibrated = CalibratedClassifierCV(raw_model, method="sigmoid", cv=3).fit(X_train, y_train)
    probability = calibrated.predict_proba(X_test)[:, 1]
    observed, predicted = calibration_curve(y_test, probability, n_bins=10, strategy="quantile")
    report = {"model_name": "XGBoost 30-Day Readmission Classifier (Week 9 tuned)", "dataset": "UCI Diabetes 130-US Hospitals", "feature_engineering": ["age-bin midpoint", "ICD-9 diagnostic categories", "one-hot encounter and medication features", "numeric feature scaling"], "class_imbalance": {"strategy": "scale_pos_weight", "value": round(weight, 4)}, "cross_validation": {"folds": 3, "metric": "roc_auc", "comparison": comparison, "selected_model": winner}, "uncalibrated_test_metrics": scores(y_test, raw_probability), "calibrated_test_metrics": scores(y_test, probability), "calibration_curve": {"mean_predicted_probability": [round(float(x), 4) for x in predicted], "fraction_of_positives": [round(float(x), 4) for x in observed]}, "note": "Calibration and external validation are required before interpreting a score as a reliable clinical probability. This prototype is decision support only."}
    joblib.dump(calibrated, os.path.join(MODELS_DIR, "xgboost_readmission_week9_calibrated.joblib"))
    with open(os.path.join(OUTPUTS_DIR, "week9_metrics.json"), "w", encoding="utf-8") as handle: json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2)); return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Use a smaller reproducible training sample")
    train_week9(parser.parse_args().quick)
