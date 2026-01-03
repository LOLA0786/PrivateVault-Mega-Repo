import os

def view_audit():
    print("📜 READING WORM AUDIT LOG (audits.worm)...")
    if os.path.exists("audits.worm"):
        with open("audits.worm", "r") as f:
            for line in f.readlines()[-5:]:
                print(f"ENTRY: {line.strip()}")
    else:
        print("⚠️ No audit log found yet. Run the demo flow first.")

if __name__ == "__main__":
    view_audit()
