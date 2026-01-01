import stripe
from fastapi import FastAPI, Header, HTTPException
from indestructible_engine import IndestructibleEngine

stripe.api_key = "sk_test_..." # Your Stripe Secret Key
app = FastAPI()
engine = IndestructibleEngine()

# In-memory usage buffer to avoid hitting Stripe on EVERY millisecond call
usage_buffer = {} 

@app.post("/optimize")
async def optimize(req: dict, x_api_key: str = Header(None)):
    # 1. Authenticate (In production, check DB for valid api_key)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Valid API Key required.")
    
    # 2. Execute Neural Logic
    val, info = engine.step(req['current_val'], req['raw_gradient'])
    
    # 3. Track Usage (Metered Billing)
    client_id = x_api_key # Simplified for this demo
    usage_buffer[client_id] = usage_buffer.get(client_id, 0) + 1
    
    # 4. Flush to Stripe every 1000 steps (Musk-style efficiency)
    if usage_buffer[client_id] >= 1000:
        stripe.billing.MeterEvent.create(
            event_name="optimization_steps",
            payload={"value": "1000", "stripe_customer_id": "cus_..."}
        )
        usage_buffer[client_id] = 0
        
    return {"optimized_value": val}
