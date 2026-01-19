"""
This our new Main instead of main.py

DATA LOADER & PREPROCESSOR
=========================
We'll Run this file ONCE to:
1. Load raw smartphone datasets
2. Clean & normalize features
3. Save reusable ML artifacts

Outputs will be :
- raw_df.pkl        (UI / explainability)
- processed_df.pkl  (ML similarity engine)
- scaler.pkl        (inference normalization)

NO Django
NO inference
NO user input
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import numpy as np
import joblib , os
from sklearn.preprocessing import MinMaxScaler


# -------------------------
# PATH CONFIGURATION
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# LOAD DATASETS
# -------------------------
def load_datasets():
    df_main = pd.read_csv(DATA_DIR / "SmartPhones.csv", encoding="latin1")
    df_extra = pd.read_csv(DATA_DIR / "smartphones_dataset_600_rows.csv", encoding="latin1")
    return df_main, df_extra


# -------------------------
# CLEAN & MERGE DATA
# -------------------------
def prepare_raw_dataframe(df, other_df):
    # Rename columns
    df = df.rename(columns={
        "Company Name": "brand",
        "Launched Price (USA)": "price",
        "Model Name": "model",
        "Mobile Weight": "weight",
        "RAM": "ram",
        "Back Camera": "cam_resolution",
        "Battery Capacity": "battery",
        "Screen Size": "display_size",
        "Launched Year": "release_year"
    })

    # Drop unused columns
    df.drop(columns=[
        "Launched Price (China)",
        "Launched Price (India)",
        "Launched Price (Pakistan)",
        "Launched Price (Dubai)",
        "Front Camera",
        "Processor"
    ], inplace=True)

    other_df = other_df.drop(columns=[
        "Model", "Brand", "Price_USD", "Camera_MP", "Battery_mAh",
        "RAM_GB", "Weight_g", "Display_Size_inch",
        "Release_Year", "Performance_Level", "Storage_GB"
    ])

    # Merge features
    df["5G"] = other_df["5G"]
    df["chipset"] = other_df["Chipset"]
    df["display_type"] = other_df["Display_Type"]

    # Select final columns
    raw_df = df[[
        "model", "brand", "price", "cam_resolution", "battery",
        "ram", "chipset", "5G", "display_size",
        "display_type", "weight", "release_year"
    ]].copy()

    # Remove duplicates
    raw_df.drop_duplicates(subset=["brand", "model"], inplace=True)

    return raw_df


# -------------------------
# FEATURE CLEANING
# -------------------------
def clean_features(df):
    df["price"] = df["price"].astype(str).str.replace(r"[^0-9]", "", regex=True).astype(float)
    df["ram"] = df["ram"].astype(str).str.extract(r"(\d+)").astype(float)
    df["battery"] = df["battery"].astype(str).str.extract(r"(\d+)").astype(float)
    df["cam_resolution"] = df["cam_resolution"].astype(str).str.extract(r"(\d+)").astype(float)
    df["display_size"] = df["display_size"].astype(str).str.extract(r"(\d+\.?\d*)").astype(float)
    df["weight"] = df["weight"].astype(str).str.extract(r"(\d+\.?\d*)").astype(float)
    df["release_year"] = df["release_year"].astype(int)
    df["5G"] = df["5G"].map({"Yes": 1, "No": 0})

    # Handle missing values
    for col in [
        "price", "ram", "battery",
        "cam_resolution", "display_size",
        "weight", "release_year"
    ]:
        df[col].fillna(df[col].median(), inplace=True)

    return df


# -------------------------
# ENCODE & SCALE
# -------------------------
def build_processed_dataframe(df):
    df_encoded = pd.get_dummies(
        df,
        columns=["brand", "display_type"],
        drop_first=True
    )

    numeric_features = [
        "price", "cam_resolution", "battery",
        "ram", "display_size", "weight", "release_year"
    ]

    scaler = MinMaxScaler()
    df_encoded[numeric_features] = scaler.fit_transform(
        df_encoded[numeric_features]
    )

    return df_encoded, scaler


# -------------------------
# MAIN PIPELINE → → → SAVE ARTIFACTS
# -------------------------
def main():
    print("🚀 Starting data preprocessing pipeline...")

    df_main, df_extra = load_datasets()
    raw_df = prepare_raw_dataframe(df_main, df_extra)
    raw_df = clean_features(raw_df)

    processed_df, scaler = build_processed_dataframe(raw_df)

    # Save artifacts
    joblib.dump(raw_df, ASSETS_DIR / "raw_df.pkl")
    joblib.dump(processed_df, ASSETS_DIR / "processed_df.pkl")
    joblib.dump(scaler, ASSETS_DIR / "scaler.pkl")

    print("✅ Artifacts created successfully:")
    print(f"   • raw_df.pkl ({raw_df.shape})")
    print(f"   • processed_df.pkl ({processed_df.shape})")
    print("   • scaler.pkl")

# -------------------------
# DJANGO RUNTIME LOADER
# -------------------------
def load_assets():
    return {
        "raw_df": joblib.load(ASSETS_DIR / "raw_df.pkl"),
        "processed_df": joblib.load(ASSETS_DIR / "processed_df.pkl"),
        "scaler": joblib.load(ASSETS_DIR / "scaler.pkl"),
    }


if __name__ == "__main__":
    main()
