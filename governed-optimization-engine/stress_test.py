import asyncio
import httpx
import time
import numpy as np

# Use 127.0.0.1 instead of localhost to skip DNS lookup (faster)
API_URL = "http://127.0.0.1:8000/optimize"
TOTAL_REQUESTS = 1000
CONCURRENCY = 20 # Lowering concurrency to prevent macOS socket exhaustion

async def main():
    print(f"🚀 Scaling Stress Test...")
    
    # Connection Pool: reuse connections to keep Success Rate high
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    async with httpx.AsyncClient(limits=limits, timeout=None) as client:
        
        latencies = []
        success_count = 0
        
        # Run in batches to respect the MacBook Air's CPU
        for i in range(0, TOTAL_REQUESTS, CONCURRENCY):
            tasks = []
            for j in range(i, min(i + CONCURRENCY, TOTAL_REQUESTS)):
                payload = {
                    "client_id": f"c_{j%5}", 
                    "metric_name": "load_test", 
                    "current_val": 100.0, 
                    "raw_gradient": 0.5
                }
                tasks.append(client.post(API_URL, json=payload))
            
            start = time.perf_counter()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = (time.perf_counter() - start) * 1000
            
            for resp in responses:
                if hasattr(resp, 'status_code') and resp.status_code == 200:
                    success_count += 1
                    latencies.append(batch_time / CONCURRENCY)

    print("\n--- STRESS TEST RESULTS ---")
    print(f"Success Rate: {(success_count/TOTAL_REQUESTS)*100:.2f}%")
    if latencies:
        print(f"Avg Latency:  {np.mean(latencies):.2f} ms")
        print(f"Throughput:   {success_count / (sum(latencies)/1000):.2f} req/sec")

if __name__ == "__main__":
    asyncio.run(main())
