import torch
import torch.nn as nn
import numpy as np

class IndestructibleEngine(nn.Module):
    def __init__(self):
        super().__init__()
        self.velocity = 0.0
        self.prev_grad = 0.0

    def step(self, current_val, grad):
        # LETHAL RESTART: If we cross the target, kill the momentum
        # This is how SpaceX rockets stabilize during landing hover
        if np.sign(grad) != np.sign(self.prev_grad):
            self.velocity *= 0.1 
            
        lr = 0.5  # Aggressive learning for low-latency
        mu = 0.9  # High momentum
        
        # Nesterov Look-Ahead
        v_prev = self.velocity
        self.velocity = (mu * v_prev) - (lr * grad)
        next_val = current_val + (mu * self.velocity) - (lr * grad)
        
        self.prev_grad = grad
        return next_val, {}
