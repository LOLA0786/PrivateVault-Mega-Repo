from galani.finance.roi import compute_roi

def run_demo():
    roi = compute_roi(12_000_000)
    print("Enterprise ROI:", roi)

if __name__ == "__main__":
    run_demo()
