def compute_roi(prevented_loss: float, system_cost: float = 250_000):
    net = prevented_loss - system_cost
    return {
        "prevented_loss": prevented_loss,
        "net_value": net,
        "roi_percent": (net / system_cost) * 100
    }
