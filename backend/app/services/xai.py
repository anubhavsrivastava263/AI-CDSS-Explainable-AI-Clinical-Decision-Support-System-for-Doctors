"""Week 10 XGBoost prediction, SHAP explanations, and reliability checks."""
from functools import lru_cache
from pathlib import Path
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parents[3]
MODELS = ROOT / "ml" / "models"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "backend" / ".mpl-cache"))
import shap


@lru_cache(maxsize=1)
def artifacts():
    model = joblib.load(MODELS / "xgboost_readmission.joblib")
    preprocessor = joblib.load(MODELS / "preprocessor.joblib")
    return model, preprocessor


def feature_row(values: dict, patient):
    model, prep = artifacts()
    names = prep["feature_names"]
    row = pd.DataFrame(np.zeros((1, len(names))), columns=names)
    age = 55
    if patient.date_of_birth:
        try: age = max(0, (pd.Timestamp.now() - pd.Timestamp(patient.date_of_birth)).days // 365)
        except (ValueError, TypeError): pass
    raw = {**values, "age_num": age}
    for name, value in raw.items():
        if name in row: row.loc[0, name] = value
    if "gender" in row: row.loc[0, "gender"] = int(patient.gender == "Male")
    numeric = prep["numeric_cols"]
    row[numeric] = prep["scaler"].transform(row[numeric])
    quality = ["Input schema matches the model feature list.", "Uncollected categorical encounter features use the training reference baseline."]
    z_scores = {name: float(abs(row.loc[0, name])) for name in numeric}
    unusual = [name for name, score in z_scores.items() if score > 3]
    warning = ("This input differs substantially from typical training data: " + ", ".join(unusual) + ". Interpret the prediction with additional caution.") if unusual else None
    return row, quality, warning


def local_explanation(values: dict, patient):
    model, _ = artifacts()
    row, quality, warning = feature_row(values, patient)
    probability = float(model.predict_proba(row)[0, 1])
    contributions = shap.TreeExplainer(model).shap_values(row)
    contributions = np.asarray(contributions).reshape(-1)
    items = [{"feature": name, "contribution": round(float(value), 4)} for name, value in zip(row.columns, contributions) if abs(value) > 0.0001]
    items.sort(key=lambda item: abs(item["contribution"]), reverse=True)
    positive = [item for item in items if item["contribution"] > 0]
    counterfactual = None
    if probability >= .5:
        for item in positive:
            if item["feature"] in values:
                alternative = {**values, item["feature"]: 0}
                alternate_row, _, _ = feature_row(alternative, patient)
                alternate_probability = float(model.predict_proba(alternate_row)[0, 1])
                if alternate_probability < .5:
                    counterfactual = f"Illustrative model behavior: if the selected input '{item['feature']}' were changed to the model reference value, this model's classification would change ({probability:.2f} to {alternate_probability:.2f}). This is not a treatment recommendation."
                    break
    return {"probability": round(probability, 4), "model_label": "XGBoost 30-day readmission model", "increasing_factors": positive[:6], "decreasing_factors": [item for item in items if item["contribution"] < 0][:6], "data_quality": quality, "ood_warning": warning, "illustrative_counterfactual": counterfactual, "disclaimer": "Model output and SHAP contributions describe model behavior only. They are not a diagnosis, prognosis, or treatment recommendation; clinician review is required."}


@lru_cache(maxsize=1)
def global_explanation():
    scripts = str(ROOT / "ml" / "scripts")
    if scripts not in sys.path: sys.path.insert(0, scripts)
    from download_or_generate_dataset import fetch_or_create_dataset
    from preprocess import preprocess_data
    model, _ = artifacts()
    _, x_test, _, y_test, _ = preprocess_data(fetch_or_create_dataset())
    sample = x_test.sample(min(250, len(x_test)), random_state=42)
    shap_values = np.asarray(shap.TreeExplainer(model).shap_values(sample))
    top = np.argsort(np.abs(shap_values).mean(axis=0))[::-1][:8]
    importance = [{"feature": sample.columns[i], "mean_abs_shap": round(float(np.abs(shap_values[:, i]).mean()), 4)} for i in top]
    perm = permutation_importance(model, sample, y_test.loc[sample.index], scoring="roc_auc", n_repeats=3, random_state=42, n_jobs=-1)
    permutation = [{"feature": sample.columns[i], "importance": round(float(perm.importances_mean[i]), 4)} for i in np.argsort(perm.importances_mean)[::-1][:8]]
    plots = {}
    for i in top[:2]:
        feature = sample.columns[i]
        base = sample[feature]
        grid = np.linspace(float(base.quantile(.05)), float(base.quantile(.95)), 10)
        pdp, ice = [], []
        for value in grid:
            changed = sample.copy(); changed[feature] = value
            pdp.append(round(float(model.predict_proba(changed)[:, 1].mean()), 4))
            ice.append([round(float(v), 4) for v in model.predict_proba(changed.iloc[:8])[:, 1]])
        plots[feature] = {"values": [round(float(v), 4) for v in grid], "pdp": pdp, "ice": ice}
    return {"global_shap": importance, "permutation_importance": permutation, "pdp_ice": plots, "calibration_note": "Probability calibration is reported by the Week 9 experiment. Validate calibration and external performance before treating any score as a reliable probability."}
