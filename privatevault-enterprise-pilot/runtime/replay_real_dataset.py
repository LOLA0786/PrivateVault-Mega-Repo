import csv
from execute_and_log import execute_and_log

DATASET = "datasets/creditcard.csv"


def replay():
    with open(DATASET) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            event = {
                "domain": "fintech",
                "actor": "shadow-replay",
                "action": "credit_transaction",
                "mode": "shadow",
                "amount": float(row["Amount"]),  # 🔥 THIS LINE
                "payload": row,
            }

            execute_and_log(event)

            if i % 1000 == 0:
                print(f"Processed {i} events")


if __name__ == "__main__":
    replay()

from shadow_mode import shadow_summary

# ---- FINAL SHADOW SUMMARY ----
summary = shadow_summary()

print("\n================ SHADOW AUDIT SUMMARY ================")
print(f"Divergences detected: {summary['divergence_count']}")
print(f"Total $ prevented: ${summary['prevented_total']:,.2f}")
print(f"High-risk examples (> $10k): {len(summary['high_risk_examples'])}")

for ex in summary["high_risk_examples"][:5]:
    print(
        f"  - Blocked ${ex['amount']:,.2f} | "
        f"Hash: {ex['intent_hash']} | "
        f"Policy: {ex['policy']}"
    )
print("======================================================")
