class IndestructibleEngine:
    def __init__(self, lr=0.01, momentum=0.9):
        self.lr, self.momentum, self.v = lr, momentum, 0

    def step(self, current_val, gradient):
        v_prev = self.v
        self.v = self.momentum * self.v - self.lr * gradient
        optimized_val = current_val + self.v + self.momentum * (self.v - v_prev)
        return float(optimized_val)
