# detection_engine.py
import os
import signal
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
SAFE_USERS = {'root', 'your_user_here'}  # do not kill important system users
SAFE_NAMES = {'systemd', 'init', 'explorer.exe', 'python', 'code'}  # tune for your OS

class Detector:
    def __init__(self, cpu_mean_threshold=40.0, spike_threshold=5, repetitive_required=True, kill=True, cooldown=30):
        self.cpu_mean_threshold = cpu_mean_threshold
        self.spike_threshold = spike_threshold
        self.repetitive_required = repetitive_required
        self.kill = kill
        self.cooldown = cooldown
        self.last_action = {}  # pid -> timestamp

    def is_suspicious(self, feat):
        # Basic rules: sustained high mean CPU and either repetitive or many spikes
        if feat['cpu_mean'] < self.cpu_mean_threshold:
            return False
        if self.repetitive_required and feat['repetitive_score'] < 1.0 and feat['spike_count'] < self.spike_threshold:
            return False
        # additional checks: avoid killing processes owned by safe users
        if feat.get('username') in SAFE_USERS:
            return False
        # avoid obvious system names (tune this list)
        if feat.get('name') and feat['name'].lower() in SAFE_NAMES:
            return False
        return True

    def act(self, features):
        actions = []
        for f in features:
            pid = f['pid']
            if self.is_suspicious(f):
                now = time.time()
                if pid in self.last_action and now - self.last_action[pid] < self.cooldown:
                    continue
                msg = f"Suspicious process {f['name']} (PID {pid}) mean_cpu={f['cpu_mean']:.1f} std={f['cpu_std']:.1f} repetitive={f['repetitive_score']}"
                logging.warning(msg)
                if self.kill:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        logging.info(f"Sent SIGTERM to PID {pid}")
                    except PermissionError:
                        logging.error(f"No permission to kill PID {pid}")
                    except ProcessLookupError:
                        logging.info(f"PID {pid} not found")
                self.last_action[pid] = now
                actions.append({'pid': pid, 'action': 'kill' if self.kill else 'alert', 'reason': msg})
        return actions
