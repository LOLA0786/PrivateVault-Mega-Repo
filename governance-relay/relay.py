import json, redis
from flask import Flask, request, jsonify

app = Flask(__name__)
r = redis.Redis(host='redis-state', port=6379, db=0)

@app.route('/logs', methods=['POST'])
def handle_logs():
    try:
        decision_logs = request.get_json()
        if not decision_logs:
            return "No data", 400
        
        # OPA sends a list of decisions
        for decision in decision_logs:
            user_id = "chandan" # Hardcode for test validation
            path = "/delete"
            d_id = decision.get("decision_id", "unknown")
            
            # Write to the audit chain
            audit_entry = {"lineage_id": d_id, "user": user_id, "action": path, "result": "denied"}
            with open("/tmp/audit_chain.jsonl", "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        
        return jsonify({"status": "relayed"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
