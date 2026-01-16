from collections import defaultdict

_METRICS = defaultdict(int)

def inc(metric_name: str):
    """Increment a metric counter."""
    _METRICS[metric_name] += 1

def snapshot():
    """Return current metrics snapshot."""
    return dict(_METRICS)
