"""
train_satisfaction_model.py

Train and save a satisfaction regressor and simple evaluation.
Outputs:
 - assets/satisfaction_model.pkl
 - (optionally) assets/satisfaction_metrics.json

This script is self-contained and uses processed_df.pkl if available.
If no ground-truth 'satisfaction' column exists, it synthesizes a proxy target
from battery/ram/cam_resolution (normalized).
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# ---------- PATHS ----------
BASE = Path(__file__).resolve().parent
ASSETS_DIR = BASE / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
PROCESSED_PATH = ASSETS_DIR / "processed_df.pkl"
RAW_PATH = ASSETS_DIR / "raw_df.pkl"
SCALER_PATH = ASSETS_DIR / "scaler.pkl"
OUT_MODEL = ASSETS_DIR / "satisfaction_model.pkl"
OUT_METRICS = ASSETS_DIR / "satisfaction_metrics.json"

# ---------- LOAD DATA ----------
if PROCESSED_PATH.exists():
    print("Loading processed_df.pkl (preferred)")
    processed = joblib.load(PROCESSED_PATH)
    # processed is expected to be normalized and include numeric features
    df = processed.copy()
else:
    # fallback to raw_df (will attempt minimal cleaning)
    if RAW_PATH.exists():
        print("processed_df not found — loading raw_df.pkl and building features")
        df = joblib.load(RAW_PATH).copy()
    else:
        raise FileNotFoundError("No processed_df.pkl or raw_df.pkl found in assets. Run data_loader first.")

# ---------- Identify features ----------
# Use canonical numeric features (these must match your data_loader)
NUMERIC_FEATURES = ["price", "cam_resolution", "battery", "ram", "display_size", "weight", "release_year"]

for feat in NUMERIC_FEATURES:
    if feat not in df.columns:
        raise KeyError(f"Expected feature '{feat}' not found in data. Found columns: {list(df.columns)[:20]}")

# ---------- TARGET ----------
# If dataset already has a column 'satisfaction' then use it.
# Otherwise synthesize a proxy target.
TARGET_COL = "satisfaction"

if TARGET_COL in df.columns:
    print("Using real 'satisfaction' column as target.")
    y = df[TARGET_COL].astype(float).values
else:
    print("No 'satisfaction' column found. Creating synthetic proxy target.")
    # proxy: weighted sum of battery, ram, cam_resolution (higher -> better),
    # price *negatively* correlated (lower price is better for satisfaction at same specs)
    # Normalize chosen columns to 0-1 for stable proxy.
    proxy_cols = ["battery", "ram", "cam_resolution", "price"]
    # compute min/max safely
    df_subset = df[proxy_cols].astype(float).copy()
    # Protect against constant columns
    min_vals = df_subset.min()
    max_vals = df_subset.max()
    range_vals = (max_vals - min_vals).replace(0, 1.0)

    df_norm = (df_subset - min_vals) / range_vals

    # weights (adjustable)
    w_batt = 0.35
    w_ram = 0.25
    w_cam = 0.25
    w_price = -0.15  # negative: cheaper is better for satisfaction given same specs

    y_proxy = (
        w_batt * df_norm["battery"]
        + w_ram * df_norm["ram"]
        + w_cam * df_norm["cam_resolution"]
        + w_price * df_norm["price"]
    )

    # rescale to 0..1
    y_min, y_max = y_proxy.min(), y_proxy.max()
    if y_max - y_min > 0:
        y = (y_proxy - y_min) / (y_max - y_min)
    else:
        y = np.clip(y_proxy, 0, 1)

# ---------- FEATURES MATRIX ----------
# If processed_df is normalized, prefer using its numeric features directly.
if PROCESSED_PATH.exists():
    X = df[NUMERIC_FEATURES].astype(float).values
else:
    # If raw_df, do simple numeric extraction and min-max scaling here for training
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    X = scaler.fit_transform(df[NUMERIC_FEATURES].astype(float).values)
    # Save this temporary scaler for later inference compatibility
    joblib.dump(scaler, ASSETS_DIR / "satisfaction_temp_scaler.pkl")

# ---------- Split ----------
RANDOM_STATE = 42
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=RANDOM_STATE)

# ---------- Train model ----------
print("Training RandomForestRegressor (satisfaction predictor)...")
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    random_state=RANDOM_STATE,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ---------- Evaluate ----------
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Cross-validated MAE (optional quick check)
cv_scores = None
try:
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="neg_mean_absolute_error", n_jobs=-1)
    cv_mae = -float(np.mean(cv_scores))
except Exception as e:
    cv_mae = None
    print("CV scoring skipped:", e)

metrics = {
    "mse": float(mse),
    "mae": float(mae),
    "r2": float(r2),
    "cv_mae": float(cv_mae) if cv_mae is not None else None,
    "train_size": int(X_train.shape[0]),
    "test_size": int(X_test.shape[0]),
}

print("Evaluation metrics:", metrics)

# ---------- Save model ----------
joblib.dump(model, OUT_MODEL)
with open(OUT_METRICS, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"Saved satisfaction model to: {OUT_MODEL}")
print(f"Saved metrics to: {OUT_METRICS}")
