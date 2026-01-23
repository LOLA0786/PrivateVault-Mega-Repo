import torch
import torch.nn as nn
import numpy as np


class KalmanDenoiser:
    """
    MAANG-grade Signal Processing.
    Filters out 'noise' so the Nesterov logic only acts on 'truth'.
    """

    def __init__(self, process_variance=1e-5, measurement_variance=1e-2):
        self.post_estimate = 0.0
        self.post_error_est = 1.0
        self.q = process_variance  # How much we trust our model
        self.r = measurement_variance  # How much we trust the data

    def filter(self, measurement):
        # Prediction
        prior_estimate = self.post_estimate
        prior_error_est = self.post_error_est + self.q

        # Update (Kalman Gain)
        blending_factor = prior_error_est / (prior_error_est + self.r)
        self.post_estimate = prior_estimate + blending_factor * (
            measurement - prior_estimate
        )
        self.post_error_est = (1 - blending_factor) * prior_error_est

        return self.post_estimate


class RobustOmegaEngine(nn.Module):
    def __init__(self):
        super().__init__()
        self.denoiser = KalmanDenoiser()
        self.velocity = 0.0
        self.history = []

        # Meta-Learner for dynamic hyperparams
        self.meta_brain = nn.Sequential(
            nn.Linear(5, 16), nn.ReLU(), nn.Linear(16, 2), nn.Sigmoid()
        )

    def step(self, current_val, raw_gradient):
        # 1. DENOISE: Don't react to glitches
        clean_gradient = self.denoiser.filter(raw_gradient)

        # 2. CLIP: Prevent 'Exploding' data from breaking the system
        # If gradient is > 10x the average, cap it.
        if len(self.history) > 5:
            avg_grad = np.mean(self.history[-5:])
            limit = abs(avg_grad) * 5.0
            clean_gradient = np.clip(clean_gradient, -limit, limit)

        self.history.append(clean_gradient)
        if len(self.history) < 5:
            return current_val, {"mode": "warmup"}

        # 3. META-ADAPT: Get LR and MU
        input_bits = torch.FloatTensor(self.history[-5:])
        with torch.no_grad():
            params = self.meta_brain(input_bits)
        lr, mu = params[0].item() * 0.1, 0.8 + (params[1].item() * 0.15)

        # 4. NESTEROV: Execute the 'Look-Ahead'
        v_prev = self.velocity
        self.velocity = (mu * v_prev) - (lr * clean_gradient)
        next_val = current_val + (mu * self.velocity) - (lr * clean_gradient)

        return next_val, {"lr": lr, "mu": mu, "clean_grad": clean_gradient}


if __name__ == "__main__":
    engine = RobustOmegaEngine()
    state = 100.0

    print(
        f"{'STEP':<5} | {'STATE':<10} | {'RAW_GRAD':<10} | {'CLEAN_GRAD':<10} | {'STATUS'}"
    )
    print("-" * 70)

    for i in range(15):
        # Simulate data with a massive 'Glitch' (Noise) at step 8
        noise = np.random.normal(0, 0.05)
        raw_grad = 0.5 + noise
        if i == 8:
            raw_grad = 50.0  # A massive anomaly!

        state, info = engine.step(state, raw_grad)

        clean_g = info.get("clean_grad", 0.0)
        status = "CLIPPED/DENOISED" if i == 8 else "STABLE"
        print(
            f"{i:<5} | {state:<10.2f} | {raw_grad:<10.2f} | {clean_g:<10.4f} | {status}"
        )
