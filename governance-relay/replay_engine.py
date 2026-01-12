import json, sys
def replay_session(target_id):
    print(f"--- STARTING REPLAY FOR ID: {target_id} ---")
    with open("/tmp/audit_chain.jsonl", "r") as f:
        for line in f:
            e = json.loads(line)
            seq = e.get('sequence_count', 'N/A')
            print(f"[{seq}] Action: {e.get('action')} | Result: {e.get('result')}")
            if str(e.get('lineage_id')) == str(target_id):
                print("\n>>> TARGET MATCH FOUND <<<")
                break
if __name__ == "__main__":
    if len(sys.argv) > 1: replay_session(sys.argv[1])
