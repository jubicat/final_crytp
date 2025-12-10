# monitoring_agent.py
import psutil
import time
from collections import defaultdict, deque
import threading

class Monitor:
    def __init__(self, interval=1.0, window=20):
        self.interval = interval
        self.window = window
        # store CPU history per pid: deque of recent cpu percents
        self.cpu_hist = defaultdict(lambda: deque(maxlen=window))
        # store last seen process info
        self.last_info = {}

    def sample_once(self):
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'create_time', 'cmdline', 'username', 'memory_percent']):
            try:
                info = p.info
                pid = info['pid']
                # `cpu_percent` requires a prior call: we rely on psutil's internal sampling (call interval-based monitor)
                cpu = info.get('cpu_percent', 0.0)
                self.cpu_hist[pid].append(cpu)
                self.last_info[pid] = {
                    'pid': pid,
                    'name': info.get('name'),
                    'cmdline': info.get('cmdline'),
                    'username': info.get('username'),
                    'create_time': info.get('create_time'),
                    'memory_percent': info.get('memory_percent'),
                    'cpu_history': list(self.cpu_hist[pid])
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def monitor_loop(self, callback=None, stop_event=None):
        """
        callback: function(process_snapshot_dict) called every tick with snapshot list
        stop_event: threading.Event to stop monitoring
        """
        if stop_event is None:
            stop_event = threading.Event()
        # Prime CPU percent by calling once (psutil needs a baseline)
        psutil.cpu_percent(interval=None)
        for p in psutil.process_iter():
            try:
                p.cpu_percent(interval=None)
            except Exception:
                pass

        while not stop_event.is_set():
            self.sample_once()
            snapshot = list(self.last_info.values())
            if callback:
                callback(snapshot)
            time.sleep(self.interval)
