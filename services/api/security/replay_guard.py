import time
from fastapi import HTTPException

# Simple in-memory replay protection
_REPLAY_CACHE = {}
_TTL_SECONDS = 300  # 5 minutes

def guard_replay(event_id: str):
    now = time.time()

    # cleanup expired entries
    expired = [k for k, v in _REPLAY_CACHE.items() if now - v > _TTL_SECONDS]
    for k in expired:
        _REPLAY_CACHE.pop(k, None)

    if event_id in _REPLAY_CACHE:
        raise HTTPException(status_code=409, detail="REPLAY_DETECTED")

    _REPLAY_CACHE[event_id] = now
