import time
import numpy as np
from indestructible_engine import IndestructibleEngine


def run_benchmark():
    engine = IndestructibleEngine()
    target = 100.0
    current = 0.0
    steps = 0
    start_time = time.time()

    # Target: Reach 100 with less than 0.01 error
    while abs(target - current) > 0.01 and steps < 1000:
        grad = current - target  # Simple gradient
        current, _ = engine.step(current, grad)
        steps += 1

    duration = (time.time() - start_time) * 1000
    print(f"--- OAAS BENCHMARK ---")
    print(f"Settling Steps: {steps}")
    print(f"Total Compute:  {duration:.2f}ms")
    print(f"Avg per Step:   {duration/steps:.4f}ms")


if __name__ == "__main__":
    run_benchmark()
