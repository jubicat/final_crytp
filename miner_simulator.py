# miner_simulator.py
import hashlib
import random
import time
import argparse
import os
import signal
import sys

def fake_miner(intensity=1.0, sleep_interval=0.0):
    """
    intensity: multiplier to increase CPU work per loop
    sleep_interval: tiny sleep to change CPU profile (0 for max CPU)
    """
    print(f"[Miner] PID={os.getpid()} Starting mining simulation (intensity={intensity}, sleep={sleep_interval})")
    try:
        while True:
            # do a configurable amount of hashing work
            work = int(1000 * intensity)
            h = b""
            for _ in range(work):
                h = hashlib.sha256(h + random.randbytes(8)).digest()
            # optionally sleep a bit to shape CPU profile
            if sleep_interval > 0:
                time.sleep(sleep_interval)
    except KeyboardInterrupt:
        print("[Miner] Exiting (KeyboardInterrupt)")
    except Exception as e:
        print("[Miner] Exception:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake miner simulator")
    parser.add_argument("--intensity", type=float, default=1.0, help="work multiplier (higher => more CPU)")
    parser.add_argument("--sleep", type=float, default=0.0, help="sleep in seconds per loop (0 => continuous CPU)")
    args = parser.parse_args()
    fake_miner(intensity=args.intensity, sleep_interval=args.sleep)
