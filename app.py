from flask import Flask, request, jsonify
from nesterov_engine import UniversalNesterovOptimizer
import numpy as np

app = Flask(__name__)

# Global registry of 'State' for different clients
# In a real MAANG setup, this would be a Redis/Vector DB
client_states = {}

@app.route('/optimize', methods=['POST'])
def universal_api():
    data = request.json
    client_id = data.get('client_id')
    metric_name = data.get('metric') # e.g., 'supply_chain', 'ad_spend', 'gpu_load'
    current_val = np.array(data.get('current_val'))
    gradient = np.array(data.get('gradient')) # The 'direction' of change

    key = f"{client_id}_{metric_name}"
    
    if key not in client_states:
        client_states[key] = UniversalNesterovOptimizer()

    optimizer = client_states[key]
    optimized_action = optimizer.optimize(current_val, gradient)

    return jsonify({
        "status": "optimized",
        "industry": data.get('industry'),
        "recommended_next_value": optimized_action.tolist(),
        "logic": "Nesterov Accelerated Look-Ahead"
    })

if __name__ == '__main__':
    print("OAAS Engine Live. Awaiting Industry Data...")
    app.run(port=5000)
