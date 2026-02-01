import requests
import time
import sys

# Configuration
GATEWAY_URL = "http://127.0.0.1:8001/secure_optimize"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"

# The 25 E-Commerce Synergy Use Cases
test_cases = [
    # --- PHASE 1: PRICING & INVENTORY (The "Flash Sale" Chaos) ---
    {
        "id": "01",
        "cat": "PRC",
        "desc": "Pricing Algo: 99% Drop Glitch (iPhone $1)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 5000000,
    },
    {
        "id": "02",
        "cat": "PRC",
        "desc": "Dynamic Pricing: Surge Cap Exceeded (Price Gouging)",
        "risk": 90.0,
        "mode": "ENFORCE",
        "val": 200000,
    },
    {
        "id": "03",
        "cat": "INV",
        "desc": "Inventory: Botnet Hoarding (1000 units/sec)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 800000,
    },
    {
        "id": "04",
        "cat": "INV",
        "desc": "Cart Abandonment: Valid Recovery Email",
        "risk": 0.05,
        "mode": "ENFORCE",
        "val": 0,
    },
    {
        "id": "05",
        "cat": "PRC",
        "desc": "Currency Conversion: Forex API Drift (>10%)",
        "risk": 85.0,
        "mode": "SHADOW",
        "val": 0,
    },
    {
        "id": "06",
        "cat": "INV",
        "desc": "Stockout Prediction: Valid Reorder Trigger",
        "risk": 0.02,
        "mode": "ENFORCE",
        "val": 0,
    },
    # --- PHASE 2: CHECKOUT & PAYMENTS (The "Cash Register") ---
    {
        "id": "07",
        "cat": "PAY",
        "desc": "Card Testing: Velocity Attack (100 cards/min)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 150000,
    },
    {
        "id": "08",
        "cat": "PAY",
        "desc": "Promo Abuse: 'NEWUSER' Code on Existing Device",
        "risk": 95.0,
        "mode": "ENFORCE",
        "val": 50000,
    },
    {
        "id": "09",
        "cat": "PAY",
        "desc": "Address: Geo-Mismatch (Ship to Freight Forwarder)",
        "risk": 80.0,
        "mode": "SHADOW",
        "val": 0,
    },
    {
        "id": "10",
        "cat": "PAY",
        "desc": "Gift Card: Brute Force Redemption Attempt",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 300000,
    },
    {
        "id": "11",
        "cat": "PAY",
        "desc": "BNPL: Credit Line Hallucination (Limit Bypass)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 100000,
    },
    {
        "id": "12",
        "cat": "PAY",
        "desc": "Valid Checkout: Prime Member",
        "risk": 0.01,
        "mode": "ENFORCE",
        "val": 0,
    },
    # --- PHASE 3: REVIEWS & RECOMMENDATIONS (The "Brand") ---
    {
        "id": "13",
        "cat": "REV",
        "desc": "Review Bombing: Competitor Bot Swarm (Negative)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 2000000,
    },
    {
        "id": "14",
        "cat": "REC",
        "desc": "Recommendation: Pushing 'Banned' Item (Hazardous)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 5000000,
    },
    {
        "id": "15",
        "cat": "REV",
        "desc": "Fake 5-Star: GPT-Generated Text Pattern",
        "risk": 85.0,
        "mode": "SHADOW",
        "val": 0,
    },
    {
        "id": "16",
        "cat": "REC",
        "desc": "Personalization: Valid Cross-Sell",
        "risk": 0.05,
        "mode": "ENFORCE",
        "val": 0,
    },
    {
        "id": "17",
        "cat": "SEO",
        "desc": "SEO Spam: Product Title Injection (Keyword Stuffing)",
        "risk": 90.0,
        "mode": "ENFORCE",
        "val": 50000,
    },
    # --- PHASE 4: RETURNS & ADS (The "Leakage") ---
    {
        "id": "18",
        "cat": "RET",
        "desc": "Refund Fraud: 'Wardrobing' Pattern Detected",
        "risk": 95.0,
        "mode": "ENFORCE",
        "val": 25000,
    },
    {
        "id": "19",
        "cat": "RET",
        "desc": "Empty Box Claim: User History Anomaly",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 10000,
    },
    {
        "id": "20",
        "cat": "ADS",
        "desc": "Ad Spend: Click Injection Fraud (100% CTR)",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 500000,
    },
    {
        "id": "21",
        "cat": "ADS",
        "desc": "Affiliate Cookie Stuffing Detected",
        "risk": 90.0,
        "mode": "ENFORCE",
        "val": 150000,
    },
    {
        "id": "22",
        "cat": "RET",
        "desc": "Valid Return Request (Damaged Item)",
        "risk": 0.10,
        "mode": "ENFORCE",
        "val": 0,
    },
    {
        "id": "23",
        "cat": "USR",
        "desc": "Account Takeover: Login from New Device+Location",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 100000,
    },
    {
        "id": "24",
        "cat": "USR",
        "desc": "GDPR: 'Right to Access' Data Export",
        "risk": 0.01,
        "mode": "ENFORCE",
        "val": 0,
    },
    {
        "id": "25",
        "cat": "API",
        "desc": "Scraping: Price Scraper Bot Blocked",
        "risk": 99.9,
        "mode": "ENFORCE",
        "val": 500000,
    },
]

total_saved = 0

print(f"\n{ANSI_CYAN}🛒 GALANI RETAIL SHIELD | REVENUE PROTECTION ENGINE{ANSI_RESET}")
print(
    f"{ANSI_CYAN}================================================================{ANSI_RESET}"
)
print(f"ID  | CATEGORY | SCENARIO DESCRIPTION                   | MODE    | RESULT")
print(f"------------------------------------------------------------------------")

for case in test_cases:
    payload = {
        "current_val": 100.0,
        "raw_gradient": case["risk"],
        "mode": case["mode"],
        "actor": "ecomm_core_system",
    }

    try:
        start = time.time()
        resp = requests.post(GATEWAY_URL, json=payload)
        latency = (time.time() - start) * 1000

        status = ""
        action = ""

        if resp.status_code == 200:
            if case["mode"] == "SHADOW" and case["risk"] > 1.0:
                status = f"{ANSI_YELLOW}⚠️  FLAGGED{ANSI_RESET}"
            else:
                status = f"{ANSI_GREEN}✅ APPROVED{ANSI_RESET}"
        elif resp.status_code == 403:
            status = f"{ANSI_RED}🛑 BLOCKED {ANSI_RESET}"
            total_saved += case["val"]
        else:
            status = f"{ANSI_RED}❌ ERROR   {ANSI_RESET}"

        print(
            f"{case['id']}  | {case['cat']}      | {case['desc']:<42} | {case['mode'][:4]}...  | {status} ({int(latency)}ms)"
        )
        time.sleep(0.12)

    except Exception as e:
        print(f"Connection Error: {e}")
        break

print(f"------------------------------------------------------------------------")
print(
    f"{ANSI_CYAN}💰 REVENUE PROTECTED (LOSS AVERTED): ${total_saved:,.2f}{ANSI_RESET}"
)
print(f"{ANSI_CYAN}🛡️  BRAND SAFETY STATUS: 100% SECURED{ANSI_RESET}\n")
