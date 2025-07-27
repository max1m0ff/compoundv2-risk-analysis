# decode_logs.py

import pandas as pd
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()
API_KEY = os.getenv("COVALENT_API_KEY")
TX_API_URL = "https://api.covalenthq.com/v1/1/transaction_v2/{tx_hash}/"

INPUT_CSV = "data/raw_transactions.csv"
OUTPUT_CSV = "data/raw_transactions_decoded.csv"

def fetch_action_from_logs(tx_hash):
    url = TX_API_URL.format(tx_hash=tx_hash)
    params = {"key": API_KEY}
    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return "unknown"

        data = resp.json()
        log_events = data.get("data", {}).get("items", [])[0].get("log_events", [])

        for log in log_events:
            decoded = log.get("decoded", {})
            if decoded:
                action_name = decoded.get("name")
                if action_name:
                    return action_name
        return "unknown"
    except Exception as e:
        print(f"Error fetching {tx_hash}: {e}")
        return "unknown"

def main():
    df = pd.read_csv(INPUT_CSV)
    update_count = 0

    for i, row in df.iterrows():
        if row["action"] == "unknown":
            tx_hash = row["tx_hash"]
            new_action = fetch_action_from_logs(tx_hash)
            if new_action != "unknown":
                df.at[i, "action"] = new_action
                update_count += 1
            time.sleep(0.2)  # Be nice to API rate limits

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Updated {update_count} unknown actions. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
