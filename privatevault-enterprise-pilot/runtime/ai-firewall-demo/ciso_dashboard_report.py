import json
import logging
from decision_ledger import (
    get_logs,
)  # Assuming existing get_logs() returns list of dicts

logging.basicConfig(level=logging.INFO)


def generate_report():
    logs = (
        get_logs()
    )  # Mock if needed: logs = [{'type': 'input_filter', 'blocked': True}, ...]
    metrics = {
        "total_requests": len(logs),
        "blocked_inputs": sum(1 for log in logs if "blocked" in log and log["blocked"]),
        "drift_blocks": sum(1 for log in logs if "drift" in log.get("reason", "")),
        "unauthorized_tools": sum(
            1 for log in logs if "unauthorized" in log.get("reason", "")
        ),
        "pii_redactions": sum(1 for log in logs if "pii" in log.get("type", "")),
        "top_threat_reasons": ["injection", "drift"],  # Aggregate logic here
        "compliance_coverage": 85,  # Mock % based on mappings
    }

    with open("dashboard_report.json", "w") as f:
        json.dump(metrics, f, indent=2)

    html = """
    <html>
    <body>
    <h1>CISO Dashboard</h1>
    <pre>{}</pre>
    </body>
    </html>
    """.format(
        json.dumps(metrics, indent=2)
    )
    with open("dashboard.html", "w") as f:
        f.write(html)

    logging.info("Dashboard generated")


if __name__ == "__main__":
    generate_report()
