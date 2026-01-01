import torch
import torch.nn as nn
import numpy as np

class UniversalPhysicsLayer:
    """
    Advanced Soft-Landing Constraints.
    Instead of hard-clamping, it applies 'resistive force' near limits.
    """
    def __init__(self, min_val=0.0):
        self.min_val = min_val

    def apply(self, x):
        # Lethal logic: If value < 5% of range, increase damping
        if x < self.min_val + 1.0:
            return max(self.min_val, x * 0.5) 
        return x

class OmegaOptimizer(nn.Module):
    def __init__(self, input_dim=5):
        super().__init__()
        self.meta_learner = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.Tanh(),
            nn.Linear(32, 2), 
            nn.Sigmoid() 
        )
        self.physics = UniversalPhysicsLayer()
        self.velocity = 0.0

    def get_params(self, history):
        # Fix: Ensure we handle tensors correctly without warnings
        input_data = torch.as_tensor(history[-5:], dtype=torch.float32)
        with torch.no_grad():
            raw_params = self.meta_learner(input_data)
        
        # Scaling params to lethal ranges
        lr = raw_params[0].item() * 0.1
        mu = 0.8 + (raw_params[1].item() * 0.15) # Momentum between 0.8 and 0.95
        return lr, mu

    def step(self, current_val, gradient, history):
        lr, mu = self.get_params(history)
        
        # Curvature Sensing (Hessian Approximation)
        curvature = abs(gradient - (history[-1] if history else 0)) + 1e-5
        
        # Adaptive Step: Slow down on high curvature (sharp turns)
        adaptive_lr = lr / (1 + curvature)
        
        # Nesterov Update
        v_prev = self.velocity
        self.velocity = (mu * v_prev) - (adaptive_lr * gradient)
        
        # Look-ahead Position
        raw_next = current_val + (mu * self.velocity) - (adaptive_lr * gradient)
        
        # Apply Physics Soft-Landing
        final_val = self.physics.apply(raw_next)
        
        return final_val, {"lr": adaptive_lr, "mu": mu, "curve": curvature}

if __name__ == "__main__":
    engine = OmegaOptimizer()
    state = 100.0
    history = [0.1, 0.1, 0.1, 0.1, 0.1]
    
    print(f"{'CYCLE':<6} | {'STATE':<10} | {'LR':<10} | {'MOMENTUM':<10} | {'CURVE'}")
    print("-" * 65)
    
    for i in range(15):
        # Simulate volatile gradient (sharp increase)
        grad = 0.5 + (i * 0.5 if i < 5 else -0.2) 
        state, m = engine.step(state, grad, history)
        history.append(grad)
        print(f"{i:<6} | {state:<10.2f} | {m['lr']:<10.4f} | {m['mu']:<10.4f} | {m['curve']:.4f}")
