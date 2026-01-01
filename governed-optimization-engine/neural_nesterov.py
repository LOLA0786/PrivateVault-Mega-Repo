import torch
import torch.nn as nn
import numpy as np

class HyperNetwork(nn.Module):
    def __init__(self):
        super(HyperNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(5, 16),
            nn.ReLU(),
            nn.Linear(16, 2),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

class NeuralNesterovEngine:
    def __init__(self):
        self.meta_brain = HyperNetwork()
        self.history = []
        self.velocity = 0.0

    def step(self, current_val, gradient):
        self.history.append(abs(gradient))
        
        # WARM-UP LOGIC: If we don't have enough history, use default MAANG constants
        if len(self.history) < 5:
            lr, mu = 0.01, 0.9
            params = {"lr": lr, "momentum": mu, "mode": "warmup"}
        else:
            # META-LEARNING: Predict optimal params from the last 5 gradients
            input_tensor = torch.FloatTensor(self.history[-5:])
            with torch.no_grad():
                predicted_params = self.meta_brain(input_tensor)
            lr, mu = predicted_params[0].item(), predicted_params[1].item()
            params = {"lr": lr, "momentum": mu, "mode": "neural"}

        # NESTEROV CORE
        v_prev = self.velocity
        self.velocity = (mu * v_prev) - (lr * gradient)
        adjustment = (mu * self.velocity) - (lr * gradient)
        new_val = current_val + adjustment
        
        return new_val, params

if __name__ == "__main__":
    engine = NeuralNesterovEngine()
    current_capacity = 100.0
    
    print(f"{'STEP':<5} | {'CAPACITY':<10} | {'LR':<8} | {'MU':<8} | {'MODE'}")
    print("-" * 50)
    
    for i in range(15):
        sim_grad = 0.5 + (i * 0.05)
        current_capacity, p = engine.step(current_capacity, sim_grad)
        print(f"{i:<5} | {current_capacity:<10.2f} | {p['lr']:<8.4f} | {p['momentum']:<8.4f} | {p['mode']}")
