
---

# 🧠 Compound Wallet Credit Scoring (V2 + V3)

This project analyzes Ethereum wallet activity on the Compound V2 and V3 protocols to assign a **credit-like score from 0 to 1000** for each wallet, based on historical on-chain behavior.

---

## 🚀 Features

* ✅ Fetches **Compound V2 and V3** transactions using the [Covalent HQ API](https://www.covalenthq.com/)
* ✅ Detects smart contract actions like `Supply`, `Borrow`, `Repay`, etc.
* ✅ Calculates wallet features: transaction count, total value, active days, wallet age
* ✅ Assigns a **score (0–1000)** using normalized heuristics

---

## 📁 Project Structure

```
.
├── data/
│   ├── wallets.csv               # Input: List of wallet addresses
│   ├── raw_transactions.csv      # Output: Fetched Compound transactions
│   ├── raw_transactions_decoded.csv # Output: Decoded logs (with actions)
│   ├── processed_data.csv        # Output: Wallet-level features
│   └── scored_wallets.csv        # Output: Final scores (0–1000)
├── fetch_data.py                 # Step 1: Fetch Compound V2+V3 transactions
├── decode_data.py                # Step 2: Decode unknown actions using logs
├── process_data.py               # Step 3: Aggregate and compute wallet features
├── score_wallets.py              # Step 4: Generate scores using weighted heuristics
├── .env                          # Contains COVALENT_API_KEY
└── README.md                     # 📄 You're here!
```

---

## 📦 Requirements

* Python 3.8+
* Covalent HQ API key (free tier is sufficient)

---

### 🛠 Install Dependencies

```bash
pip install pandas python-dotenv requests
```

---

## 🔐 .env Configuration

Create a `.env` file in your root directory:

```
COVALENT_API_KEY=your_api_key_here
```

You can get a free API key from [Covalent HQ](https://goldrush.dev/platform/apikey/).

---

## 🔍 Step-by-Step Breakdown

---

### 1️⃣ Fetch Compound Transactions — `fetch_data.py`

📌 **Goal:** Retrieve all **Compound V2 and V3** transactions for a list of wallet addresses.

✅ **What it does:**

* Reads wallet addresses from `data/wallets.csv`.
* Uses the **Covalent HQ API** to fetch **all token transactions** per wallet:

  * Endpoint used:

    ```
    https://api.covalenthq.com/v1/{chain_id}/address/{wallet}/transactions_v2/
    ```
  * Only supports `Ethereum` (chain ID: `1`).
* Filters transactions where:

  * `to` or `from` address matches known **Compound V2 and V3 contract addresses**, like `cETH`, `cUSDC`, `Comet`, etc.
* Writes the result to `data/raw_transactions.csv`.

✅ **Why Covalent?**

* Covalent provides pre-decoded Ethereum transactions with minimal setup.
* It handles EVM decoding, token transfers, log indexing, and contract metadata — saving you from building a raw parser.
* API key is stored in `.env` for security and loaded using `python-dotenv`.

---

### 2️⃣ Decode Logs and Classify Actions — `decode_data.py`

📌 **Goal:** Identify and label unknown transaction `actions` from the raw log data.

✅ **What it does:**

* Reads `data/raw_transactions.csv`.
* For each transaction with an empty or unknown `action`:

  * Uses **Covalent’s log decoding API**:

    ```
    https://api.covalenthq.com/v1/{chain_id}/transaction_v2/{tx_hash}/
    ```
  * Parses event logs to extract method calls like:

    * `Borrow`, `Mint`, `RepayBorrow`, `Redeem`, `LiquidateBorrow`, etc.
* Adds a new column `action` to describe the transaction.
* Saves updated data to `data/raw_transactions_decoded.csv`.
* Many DeFi smart contract transactions can’t be understood by just looking at `from`, `to`, and `value`.
* Event logs contain function signatures and arguments which Covalent decodes for you.
* This step gives **semantic meaning** to each transaction, crucial for behavior modeling.

---

### 3️⃣ Process Wallet Data — `process_data.py`

📌 **Goal:** Turn raw transactions into structured wallet-level features.

✅ **What it does:**

* Reads `data/raw_transactions_decoded.csv`.
* For each wallet:

  * Counts total number of Compound transactions (`tx_count`).
  * Sums total value of transactions (`total_value` in wei).
  * Calculates:

    * `first_tx`: earliest transaction timestamp.
    * `last_tx`: most recent timestamp.
    * `active_days`: number of unique days with activity.
* Saves the final aggregated data to `data/processed_data.csv`.
* These features (volume, activity span, frequency) help estimate a wallet’s **credibility** and **engagement**.
* Normalized features allow comparison across wallets with different patterns.

---

### 4️⃣ Score Wallets — `score_wallets.py`

📌 **Goal:** Assign a **0–1000 score** per wallet based on DeFi behavior.

✅ **What it does:**

* Loads `data/processed_data.csv`.
* Normalizes each feature:

  * `tx_count`, `total_value`, `active_days`, and wallet age (`last_tx - first_tx`)
* Applies weighted scoring formula:

## 🧮 Scoring Logic

| Feature           | Weight |
| ----------------- | ------ |
| Transaction Count | 30%    |
| Total Value       | 30%    |
| Active Days       | 20%    |
| Wallet Age        | 20%    |

* Final score = Weighted average × 1000.
* Writes scores to `data/scored_wallets.csv`.
* This scoring system mimics a **credit score**:
  * More active, older, higher-volume users score higher.
  * Low-activity or one-off wallets score lower.
* Results can be used for DeFi lending risk models, wallet reputation systems, or even airdrop targeting.

---

## 📊 Example Output

`data/scored_wallets.csv`:

```
wallet_id,score
0xabc123...,742
0xdef456...,122
```

---

## 📌 Notes

* Rate-limiting: `decode_data.py` includes a short delay to respect Covalent’s API rate limits.
* All data is filtered to only include interactions with known Compound contracts.
* You can customize scoring weights in `score_wallets.py` as needed.

---

## 📃 License

MIT License — feel free to use, modify, and share.

---
