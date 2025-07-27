import pandas as pd
from datetime import datetime

def normalize(value, min_val, max_val):
    """Min-max normalization"""
    return (value - min_val) / (max_val - min_val) if max_val != min_val else 0

def calculate_score(row, max_vals, min_vals):
    tx_score = normalize(row['tx_count'], min_vals['tx_count'], max_vals['tx_count'])
    value_score = normalize(float(row['total_value']), min_vals['total_value'], max_vals['total_value'])
    active_score = normalize(row['active_days'], min_vals['active_days'], max_vals['active_days'])
    wallet_age_days = (pd.to_datetime(row['last_tx']) - pd.to_datetime(row['first_tx'])).days
    age_score = normalize(wallet_age_days, min_vals['wallet_age_days'], max_vals['wallet_age_days'])

    final_score = (
        0.3 * tx_score +
        0.3 * value_score +
        0.2 * active_score +
        0.2 * age_score
    ) * 1000

    return round(final_score)

def main():
    df = pd.read_csv("data/processed_data.csv")
    df['total_value'] = df['total_value'].astype(float)

    df['wallet_age_days'] = (
        pd.to_datetime(df['last_tx']) - pd.to_datetime(df['first_tx'])
    ).dt.days

    max_vals = df[['tx_count', 'total_value', 'active_days', 'wallet_age_days']].max()
    min_vals = df[['tx_count', 'total_value', 'active_days', 'wallet_age_days']].min()

    df['score'] = df.apply(calculate_score, axis=1, args=(max_vals, min_vals))

    final_df = df[['wallet']].copy()
    final_df.columns = ['wallet_id']
    final_df['score'] = df['score']

    final_df.to_csv("data/scored_wallets.csv", index=False)
    print("✅ Output saved to 'scored_wallets.csv'")

if __name__ == "__main__":
    main()
