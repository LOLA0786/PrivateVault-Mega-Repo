import json
import logging
from decision_ledger import get_logs
from compliance_mapper import map_event_to_controls

logging.basicConfig(level=logging.INFO)

def generate_report():
    logs = get_logs()
    threat_reasons = [log.get('reason', '') for log in logs if 'reason' in log]
    top_threats = list(set(threat_reasons))[:5]
    
    # Compliance coverage: % of logs with tags
    tagged_logs = sum(1 for log in logs if log.get('compliance_tags'))
    coverage = (tagged_logs / len(logs) * 100) if logs else 0
    
    metrics = {
        'total_requests': len(logs),
        'blocked_inputs': sum(1 for log in logs if log.get('status') == 'blocked' or 'blocked' in log.get('type', '')),
        'drift_blocks': sum(1 for log in logs if 'drift' in log.get('type', '') or 'drift' in log.get('reason', '')),
        'unauthorized_tools': sum(1 for log in logs if 'unauthorized' in log.get('reason', '')),
        'pii_redactions': sum(1 for log in logs if 'pii' in log.get('type', '')),
        'top_threat_reasons': top_threats,
        'compliance_coverage': f"{coverage:.1f}%"
    }
    
    with open('dashboard_report.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    html = """
    <html>
    <body>
    <h1>CISO Dashboard</h1>
    <pre>{}</pre>
    </body>
    </html>
    """.format(json.dumps(metrics, indent=2))
    with open('dashboard.html', 'w') as f:
        f.write(html)
    
    logging.info("Dashboard generated")

if __name__ == "__main__":
    generate_report()
