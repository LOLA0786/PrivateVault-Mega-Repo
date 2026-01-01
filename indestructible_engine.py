import torch
import torch.nn as nn
import numpy as np

class AdaptiveKalman:
    def __init__(self):
        self.estimate = 0.0
        self.error_est = 1.0
        self.q = 1e-5 # Process variance
        self.r = 1e-2 # Measurement variance (Trust in data)

    def filter(self, measurement):
        # RESIDUAL MONITORING: If data is consistently different, adapt faster
        residual = abs(measurement - self.estimate)
        dynamic_r = self.r / (1 + residual * 2.0) # Reduce 'r' if change is real
        
        # Standard Kalman Logic
        self.error_est += self.q
        gain = self.error_est / (self.error_est + dynamic_r)
        self.estimate = self.estimate + gain * (measurement - self.estimate)
        self.error_est = (1 - gain) * self.error_est
        
        return self.estimate

class IndestructibleEngine(nn.Module):
    def __init__(self):
        super().__init__()
        self.denoiser = AdaptiveKalman()
        self.velocity = 0.0
        self.history = []

    def step(self, current_val, raw_gradient):
        # 1. Adaptive Denoising (No more lag!)
        clean_gradient = self.denoiser.filter(raw_gradient)
        
        # 2. Gradient Memory
        self.history.append(clean_gradient)
        if len(self.history) < 3: return current_val, {"mode": "warmup"}

        # 3. Lethal Nesterov Hyperparams
        # We use a fixed high-performance 'Golden Ratio' for momentum
        lr, mu = 0.05, 0.92 

        # 4. Execute the Step
        v_prev = self.velocity
        self.velocity = (mu * v_prev) - (lr * clean_gradient)
        next_val = current_val + (mu * self.velocity) - (lr * clean_gradient)
        
        return next_val, {"clean_grad": clean_gradient}

if __name__ == "__main__":
    engine = IndestructibleEngine()
    state = 100.0
    
    print(f"{'STEP':<5} | {'STATE':<10} | {'RAW_GRAD':<10} | {'CLEAN_GRAD':<10}")
    print("-" * 55)
    
    for i in range(15):
        # Simulate a crash (Step 5) and a fast recovery (Step 10)
        raw_grad = 0.5
        if i == 5: raw_grad = 20.0  # The Anomaly
        if i >= 10: raw_grad = -5.0 # The Pivot (Market Reversal)
        
        state, info = engine.step(state, raw_grad)
        cg = info.get('clean_grad', 0.0)
        print(f"{i:<5} | {state:<10.2f} | {raw_grad:<10.2f} | {cg:<10.4f}")
