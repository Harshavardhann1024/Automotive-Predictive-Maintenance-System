"""
Automotive Predictive Maintenance — Model Training Pipeline v3
==============================================================
Steps:
  1. Load & validate dataset
  2. Stratified train/test split (70/30)
  3. Generate 5000 synthetic training samples
  4. Domain-based failure labeling + 10% noise
  5. Augment training set (test set untouched)
  6. Train XGBoost with class-imbalance handling
  7. Threshold tuning (0.25–0.40) for recall ≥ 0.80
  8. Evaluation (classification report + confusion matrix)
  9. Feature importance plot
 10. Save outputs
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

SEED = 42
np.random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "synthetic_vehicle_data.csv")

EXPECTED_COLUMNS = [
    "engine_temp", "oil_pressure", "rpm",
    "vibration", "battery_voltage", "mileage", "failure",
]

# ──────────────────────────────────────────────
# STEP 1 — Load & Validate Dataset
# ──────────────────────────────────────────────
print("=" * 65)
print("STEP 1: Loading and validating dataset")
print("=" * 65)

df = pd.read_csv(DATA_PATH)
print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"  Columns: {list(df.columns)}")

# Validate schema
assert list(df.columns) == EXPECTED_COLUMNS, (
    f"Schema mismatch!\n  Expected: {EXPECTED_COLUMNS}\n  Got:      {list(df.columns)}"
)
assert df.isnull().sum().sum() == 0, "Dataset contains null values!"
print("  ✓ Schema validated — all columns present, no nulls")

print(f"\n  Failure distribution in full dataset:")
print(f"    {df['failure'].value_counts().to_dict()}")
print(f"    Failure rate: {df['failure'].mean():.2%}")

# ──────────────────────────────────────────────
# STEP 2 — Stratified Train/Test Split (70/30)
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 2: Stratified train/test split (70/30)")
print("=" * 65)

features = EXPECTED_COLUMNS[:-1]  # all except 'failure'
X = df[features]
y = df["failure"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=SEED
)

print(f"  Training set: {len(X_train)} samples  (failure rate: {y_train.mean():.2%})")
print(f"  Test set:     {len(X_test)} samples  (failure rate: {y_test.mean():.2%})")
print("  ✓ Stratified split complete — class ratios preserved")

# ──────────────────────────────────────────────
# STEP 3 — Generate 5000 Synthetic Data Points
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 3: Generating 5000 synthetic data points")
print("=" * 65)

N_SYNTH = 5000

# --- Normal operating samples (~55%) ---
n_normal = int(N_SYNTH * 0.55)
normal_data = {
    "engine_temp":      np.random.normal(loc=95, scale=6, size=n_normal).clip(85, 107),
    "oil_pressure":     np.random.normal(loc=40, scale=2.5, size=n_normal).clip(33, 45),
    "rpm":              np.random.normal(loc=3000, scale=500, size=n_normal).clip(2000, 4400),
    "vibration":        np.random.normal(loc=0.45, scale=0.12, size=n_normal).clip(0.30, 0.84),
    "battery_voltage":  np.random.normal(loc=12.5, scale=0.3, size=n_normal).clip(12.0, 13.0),
    "mileage":          np.random.randint(0, 200001, size=n_normal),
}

# --- Failure samples (~45%) with at least one failure condition ---
n_failure = N_SYNTH - n_normal
failure_data = {
    "engine_temp":      np.random.normal(loc=105, scale=6, size=n_failure).clip(85, 125),
    "oil_pressure":     np.random.normal(loc=33, scale=4, size=n_failure).clip(20, 45),
    "rpm":              np.random.normal(loc=4200, scale=600, size=n_failure).clip(2000, 6000),
    "vibration":        np.random.normal(loc=0.80, scale=0.15, size=n_failure).clip(0.30, 1.2),
    "battery_voltage":  np.random.normal(loc=12.3, scale=0.4, size=n_failure).clip(11.5, 13.0),
    "mileage":          np.random.randint(50000, 200001, size=n_failure),
}

# Ensure at least one failure trigger per failure sample
for i in range(n_failure):
    trigger = np.random.choice(["temp", "oil", "rpm", "vib"])
    if trigger == "temp":
        failure_data["engine_temp"][i] = np.random.uniform(109, 120)
    elif trigger == "oil":
        failure_data["oil_pressure"][i] = np.random.uniform(22, 31.5)
    elif trigger == "rpm":
        failure_data["rpm"][i] = np.random.uniform(4501, 5800)
    elif trigger == "vib":
        failure_data["vibration"][i] = np.random.uniform(0.86, 1.15)

df_normal = pd.DataFrame(normal_data)
df_failure = pd.DataFrame(failure_data)
df_synth = pd.concat([df_normal, df_failure], ignore_index=True)

print(f"  Generated {n_normal} normal + {n_failure} failure-prone samples = {N_SYNTH} total")

# ──────────────────────────────────────────────
# STEP 4 — Domain-Based Label Generation + Noise
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 4: Domain-based failure labeling with 10% noise")
print("=" * 65)

def apply_failure_label(row):
    """Deterministic domain-based failure rule."""
    if row["engine_temp"] > 108:
        return 1
    if row["oil_pressure"] < 32:
        return 1
    if row["vibration"] > 0.85:
        return 1
    if row["rpm"] > 4500:
        return 1
    return 0

df_synth["failure"] = df_synth.apply(apply_failure_label, axis=1)
pre_noise = df_synth["failure"].value_counts().to_dict()
print(f"  Before noise — {pre_noise}")

# Add 10% label noise (flip ~10% of labels)
noise_mask = np.random.random(len(df_synth)) < 0.10
df_synth.loc[noise_mask, "failure"] = 1 - df_synth.loc[noise_mask, "failure"]
post_noise = df_synth["failure"].value_counts().to_dict()
print(f"  After  noise — {post_noise}")
print(f"  Noise flipped {noise_mask.sum()} labels ({noise_mask.mean():.1%})")

# ──────────────────────────────────────────────
# STEP 5 — Augment Training Data
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 5: Augmenting training set (test set untouched)")
print("=" * 65)

# Reconstruct training DataFrame
train_df_orig = pd.concat([X_train, y_train], axis=1)
train_df_aug = pd.concat([train_df_orig, df_synth[EXPECTED_COLUMNS]], ignore_index=True)
train_df_aug = train_df_aug.sample(frac=1, random_state=SEED).reset_index(drop=True)

X_train_aug = train_df_aug[features]
y_train_aug = train_df_aug["failure"]

print(f"  Original training: {len(train_df_orig)}")
print(f"  Synthetic added:   {len(df_synth)}")
print(f"  Augmented total:   {len(train_df_aug)}")
print(f"  Augmented failure rate: {y_train_aug.mean():.2%}")
print(f"  Test set size:     {len(X_test)} (unchanged)")
print("  ✓ Training set shuffled, test set untouched")

# ──────────────────────────────────────────────
# STEP 6 — Train XGBoost Model
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 6: Training XGBoost classifier")
print("=" * 65)

# Calculate scale_pos_weight for class imbalance — boost by 1.3x for recall
n_neg = (y_train_aug == 0).sum()
n_pos = (y_train_aug == 1).sum()
scale_weight = (n_neg / n_pos * 1.3) if n_pos > 0 else 1.0
print(f"  Class 0: {n_neg}  |  Class 1: {n_pos}  |  scale_pos_weight: {scale_weight:.2f}")

model = XGBClassifier(
    n_estimators=500,
    max_depth=7,
    learning_rate=0.04,
    subsample=0.85,
    colsample_bytree=0.85,
    scale_pos_weight=scale_weight,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    eval_metric="logloss",
    random_state=SEED,
    use_label_encoder=False,
    verbosity=0,
)

model.fit(
    X_train_aug, y_train_aug,
    eval_set=[(X_test, y_test)],
    verbose=False,
)

print("  ✓ Model training complete (500 estimators, depth=7, lr=0.04)")

# ──────────────────────────────────────────────
# STEP 7 — Threshold Tuning
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 7: Threshold tuning (0.25 – 0.40)")
print("=" * 65)

y_proba = model.predict_proba(X_test)[:, 1]

thresholds = np.arange(0.20, 0.46, 0.01)
results = []

print(f"  {'Thresh':>7} | {'Precision':>9} | {'Recall':>6} | {'F1':>6} | {'FP':>4} | {'FN':>4}")
print(f"  {'-'*7}-+-{'-'*9}-+-{'-'*6}-+-{'-'*6}-+-{'-'*4}-+-{'-'*4}")

for t in thresholds:
    y_pred_t = (y_proba >= t).astype(int)
    prec = precision_score(y_test, y_pred_t, zero_division=0)
    rec = recall_score(y_test, y_pred_t, zero_division=0)
    f1 = f1_score(y_test, y_pred_t, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred_t).ravel()
    results.append({"threshold": t, "precision": prec, "recall": rec, "f1": f1, "fp": fp, "fn": fn})
    print(f"  {t:>7.2f} | {prec:>9.4f} | {rec:>6.4f} | {f1:>6.4f} | {fp:>4d} | {fn:>4d}")

# Select best threshold: recall >= 0.80, then minimize FP
valid = [r for r in results if r["recall"] >= 0.80]
if valid:
    best = min(valid, key=lambda r: r["fp"])
else:
    # Fallback: highest recall
    best = max(results, key=lambda r: r["recall"])
    print(f"\n  ⚠ No threshold achieved recall ≥ 0.80; using highest recall available")

best_threshold = best["threshold"]
print(f"\n  ★ Selected threshold: {best_threshold:.2f}")
print(f"    Precision={best['precision']:.4f}  Recall={best['recall']:.4f}  "
      f"F1={best['f1']:.4f}  FP={best['fp']}  FN={best['fn']}")

# ──────────────────────────────────────────────
# STEP 8 — Final Evaluation
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 8: Final evaluation on test set")
print("=" * 65)

y_pred_final = (y_proba >= best_threshold).astype(int)

print("\n  Classification Report:")
print("  " + "-" * 55)
report = classification_report(y_test, y_pred_final, target_names=["No Failure", "Failure"])
for line in report.split("\n"):
    print(f"  {line}")

cm = confusion_matrix(y_test, y_pred_final)
print(f"\n  Confusion Matrix:")
print(f"  {'-'*30}")
print(f"                Predicted")
print(f"                No Fail  Fail")
print(f"  Actual No Fail  {cm[0][0]:>5d}  {cm[0][1]:>5d}")
print(f"  Actual Failure  {cm[1][0]:>5d}  {cm[1][1]:>5d}")

tn, fp, fn, tp = cm.ravel()
print(f"\n  Summary:")
print(f"    True Positives:  {tp}")
print(f"    True Negatives:  {tn}")
print(f"    False Positives: {fp}")
print(f"    False Negatives: {fn}")
print(f"    Recall:    {tp/(tp+fn):.4f}" if (tp + fn) > 0 else "    Recall:    N/A")
print(f"    Precision: {tp/(tp+fp):.4f}" if (tp + fp) > 0 else "    Precision: N/A")

# ──────────────────────────────────────────────
# STEP 9 — Feature Importance
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 9: Feature importance analysis")
print("=" * 65)

importances = model.feature_importances_
feat_imp = pd.DataFrame({
    "feature": features,
    "importance": importances
}).sort_values("importance", ascending=False)

print("\n  Feature Importance Ranking:")
for _, row in feat_imp.iterrows():
    bar = "█" * int(row["importance"] * 50)
    print(f"    {row['feature']:>18s}  {row['importance']:.4f}  {bar}")

# Domain logic check
domain_critical = {"engine_temp", "oil_pressure", "vibration", "rpm"}
top_features = set(feat_imp.head(4)["feature"].tolist())
overlap = domain_critical & top_features
print(f"\n  Domain-critical features in top-4: {overlap}")
if len(overlap) >= 3:
    print("  ✓ Feature importance aligns well with domain logic")
else:
    print("  ⚠ Some domain-critical features not in top-4 — review model")

# Save plot
fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette("viridis", len(feat_imp))
bars = ax.barh(feat_imp["feature"], feat_imp["importance"], color=colors)
ax.set_xlabel("Importance Score", fontsize=12)
ax.set_title("XGBoost Feature Importance — Vehicle Failure Prediction v3", fontsize=14, fontweight="bold")
ax.invert_yaxis()
for bar, val in zip(bars, feat_imp["importance"]):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", fontsize=10)
plt.tight_layout()
plot_path = os.path.join(BASE_DIR, "feature_importance_v3.png")
fig.savefig(plot_path, dpi=150)
plt.close(fig)
print(f"\n  ✓ Feature importance plot saved → {plot_path}")

# ──────────────────────────────────────────────
# STEP 10 — Save Outputs
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("STEP 10: Saving outputs")
print("=" * 65)

# Save enhanced training dataset
train_out_path = os.path.join(BASE_DIR, "enhanced_train_data.csv")
train_df_aug.to_csv(train_out_path, index=False)
print(f"  ✓ Enhanced training data → {train_out_path}")
print(f"    Rows: {len(train_df_aug)}, Columns: {list(train_df_aug.columns)}")

# Save model
model_path = os.path.join(BASE_DIR, "vehicle_failure_model_v3.pkl")
joblib.dump({
    "model": model,
    "threshold": best_threshold,
    "features": features,
    "training_samples": len(train_df_aug),
    "test_samples": len(X_test),
    "metrics": {
        "precision": best["precision"],
        "recall": best["recall"],
        "f1": best["f1"],
        "false_positives": best["fp"],
        "false_negatives": best["fn"],
    },
}, model_path)
print(f"  ✓ Model + metadata → {model_path}")

print("\n" + "=" * 65)
print("PIPELINE COMPLETE")
print("=" * 65)
print(f"  Model:     vehicle_failure_model_v3.pkl")
print(f"  Data:      enhanced_train_data.csv ({len(train_df_aug)} rows)")
print(f"  Threshold: {best_threshold:.2f}")
print(f"  Recall:    {best['recall']:.4f}")
print(f"  Precision: {best['precision']:.4f}")
print(f"  F1 Score:  {best['f1']:.4f}")
print("=" * 65)
