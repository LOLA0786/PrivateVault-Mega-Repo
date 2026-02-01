import subprocess, sys

def main():
    print("Running PrivateVaultAgentInterop verification suite...")
    r = subprocess.run(["pytest", "-q"], check=False)
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
