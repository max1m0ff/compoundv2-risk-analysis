# process_data.py

import pandas as pd

INPUT_CSV = "data/raw_transactions.csv"
OUTPUT_CSV = "data/processed_data.csv"

def process_data():
    df = pd.read_csv(INPUT_CSV)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Group by wallet and extract features
    features = df.groupby("wallet").agg(
        tx_count=("tx_hash", "count"),
        total_value=("value", lambda x: x.astype(float).sum()),
        first_tx=("timestamp", "min"),
        last_tx=("timestamp", "max")
    ).reset_index()

    features["active_days"] = (features["last_tx"] - features["first_tx"]).dt.days + 1
    features.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved processed data to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_data()
