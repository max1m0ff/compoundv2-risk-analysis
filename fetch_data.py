# fetch_data.py

import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Constants
COVALENT_API_KEY = os.getenv("COVALENT_API_KEY")
CHAIN_ID = 1  # Ethereum mainnet
BASE_URL = "https://api.covalenthq.com/v1"
WALLETS_CSV = "data/wallets.csv"
OUTPUT_CSV = "data/raw_transactions.csv"

# Compound V2 cToken + Unitroller contracts
COMPOUND_V2_CONTRACTS = {
    "cDAI": "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643",
    "cUSDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
    "cETH": "0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5",
    "cWBTC": "0xccf4429db6322d5c611ee964527d42e5d685dd6a",
    "Unitroller": "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"
}

# Compound V3 Comet contracts
COMPOUND_V3_CONTRACTS = {
    "Comet_USDC": "0xc3d688b66703497daa19211eedff47f25384cdc3",
    "Comet_WETH": "0xa17581a9e3356d9a858b789d68b4d866e593ae94",
    "Comet_WBTC": "0x2ee80614ccbc5e28654324a66a396458fa5cd7cc"
}

# Merge all known Compound contract addresses into one lowercase set
compound_addresses_lower = set(
    [addr.lower() for addr in list(COMPOUND_V2_CONTRACTS.values()) + list(COMPOUND_V3_CONTRACTS.values())]
)

def fetch_wallet_transactions(wallet):
    url = f"{BASE_URL}/{CHAIN_ID}/address/{wallet}/transactions_v2/"
    params = {"key": COVALENT_API_KEY, "page-size": 10000}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()
    return data["data"]["items"]

def main():
    df_wallets = pd.read_csv(WALLETS_CSV)
    all_data = []

    for wallet in df_wallets["wallet"]:
        print(f"🔍 Fetching transactions for: {wallet}")
        try:
            transactions = fetch_wallet_transactions(wallet)
            for tx in transactions:
                to_addr = tx["to_address"]
                if to_addr and to_addr.lower() in compound_addresses_lower:
                    decoded = tx.get("decoded", {})
                    action = decoded.get("name", "unknown") if decoded else "unknown"

                    all_data.append({
                        "wallet": wallet,
                        "tx_hash": tx["tx_hash"],
                        "timestamp": tx["block_signed_at"],
                        "from": tx["from_address"],
                        "to": tx["to_address"],
                        "contract_label": tx.get("to_address_label", "Compound"),
                        "action": action,
                        "value": tx["value"]
                    })

        except Exception as e:
            print(f"❌ Error for wallet {wallet}: {e}")

    # Save to CSV
    if all_data:
        df_out = pd.DataFrame(all_data)
        df_out.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ Saved {len(df_out)} Compound transactions to {OUTPUT_CSV}")
    else:
        print("\n⚠️ No Compound transactions found.")

if __name__ == "__main__":
    main()
