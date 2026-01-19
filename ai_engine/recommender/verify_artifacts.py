import joblib
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

raw_df = joblib.load(ASSETS_DIR / "raw_df.pkl")
processed_df = joblib.load(ASSETS_DIR / "processed_df.pkl")
scaler = joblib.load(ASSETS_DIR / "scaler.pkl")

print("RAW DF")
print(raw_df.head())
print("\nRAW DF SHAPE:", raw_df.shape)

print("\nPROCESSED DF")
print(processed_df.head())
print("\nPROCESSED DF SHAPE:", processed_df.shape)

print("\nScaler type:", type(scaler))
