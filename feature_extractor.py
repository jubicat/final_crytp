# feature_extractor.py
import numpy as np
import time

def summarize_cpu_history(cpu_history):
    if not cpu_history:
        return {
            'mean': 0.0,
            'max': 0.0,
            'std': 0.0,
            'spike_count': 0,
            'last': 0.0
        }
    arr = np.array(cpu_history, dtype=float)
    spike_threshold = 50.0  # percent
    spike_count = int(np.sum(arr > spike_threshold))
    return {
        'mean': float(np.mean(arr)),
        'max': float(np.max(arr)),
        'std': float(np.std(arr)),
        'spike_count': spike_count,
        'last': float(arr[-1])
    }

def extract_features(process_snapshot):
    """
    process_snapshot: list of process info dicts from Monitor.last_info
    Returns: list of dicts with features for each process
    """
    features = []
    now = time.time()
    for p in process_snapshot:
        cpu_hist = p.get('cpu_history', [])
        s = summarize_cpu_history(cpu_hist)
        age = None
        if p.get('create_time'):
            age = now - p['create_time']
        # repetitive loop indicator: low std but high mean implies steady CPU (common for miners)
        repetitive_score = 0.0
        if s['mean'] > 30 and s['std'] < max(5.0, s['mean'] * 0.1):
            repetitive_score = 1.0
        features.append({
            'pid': p['pid'],
            'name': p['name'],
            'cmdline': p.get('cmdline'),
            'username': p.get('username'),
            'age': age,
            'cpu_mean': s['mean'],
            'cpu_max': s['max'],
            'cpu_std': s['std'],
            'spike_count': s['spike_count'],
            'last_cpu': s['last'],
            'repetitive_score': repetitive_score,
            'memory_percent': p.get('memory_percent', 0.0)
        })
    return features
