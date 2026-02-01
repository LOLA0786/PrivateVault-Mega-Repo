import asyncio
import json
import httpx
import websockets
import ssl
import certifi

API_URL = "http://127.0.0.1:8000/optimize"
BINANCE_WS = "wss://stream.binance.com:9443/ws/btcusdt@depth5"


async def stream_to_engine():
    print("🛡️ Connecting to Stream with Active Risk Monitoring...")
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    last_predicted = None

    async with websockets.connect(BINANCE_WS, ssl=ssl_context) as ws:
        async with httpx.AsyncClient() as client:
            while True:
                data = json.loads(await ws.recv())
                mid_price = (float(data["bids"][0][0]) + float(data["asks"][0][0])) / 2
                bid_vol = sum([float(v[1]) for v in data["bids"]])
                ask_vol = sum([float(v[1]) for v in data["asks"]])
                obi = (bid_vol - ask_vol) / (bid_vol + ask_vol)

                payload = {
                    "client_id": "hft_unit_01",
                    "metric_name": "BTC_LOB_IMBALANCE",
                    "current_val": mid_price,
                    "raw_gradient": obi,
                    "actual_last_val": mid_price,  # For risk check
                }

                try:
                    resp = await client.post(API_URL, json=payload)
                    r_json = resp.json()

                    if "EMERGENCY_SHUTDOWN" in str(r_json):
                        print("🛑 SYSTEM HALTED: High Prediction Error Detected.")
                        break

                    future_price = r_json["optimized_value"]
                    print(
                        f"Price: {mid_price:.2f} | Forecast: {future_price:.2f} | OBI: {obi:+.2f}"
                    )

                except Exception as e:
                    pass


if __name__ == "__main__":
    asyncio.run(stream_to_engine())
