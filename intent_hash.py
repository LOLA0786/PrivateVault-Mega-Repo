import hashlib
import sys

def hash_payload(payload):
    h = hashlib.sha256(payload.encode()).hexdigest()
    print(f'{{"intent_hash": "0x{h}"}}')

if __name__ == "__main__":
    payload = sys.argv[1] if len(sys.argv) > 1 else "DEFAULT_INTENT"
    hash_payload(payload)
