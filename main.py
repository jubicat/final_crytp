# main.py
import threading
import time
from monitoring_agent import Monitor
from feature_extractor import extract_features
from detection_engine import Detector

def on_snapshot(snapshot, detector):
    feats = extract_features(snapshot)
    actions = detector.act(feats)
    for a in actions:
        print("[MAIN] Action:", a)

def run_main(interval=1.0, window=20):
    monitor = Monitor(interval=interval, window=window)
    detector = Detector(cpu_mean_threshold=40.0, spike_threshold=3, repetitive_required=True, kill=False, cooldown=30)
    stop_event = threading.Event()

    def callback(snapshot):
        on_snapshot(snapshot, detector)

    try:
        monitor.monitor_loop(callback=callback, stop_event=stop_event)
    except KeyboardInterrupt:
        print("Stopping monitor...")

if __name__ == "__main__":
    run_main()
