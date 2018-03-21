from numpy import percentile

def compute_distribution(stats):
    try:
        distribution = {}
        distribution["min"] = min(stats)
        distribution["p50"] = percentile(stats, 50)
        distribution["p99"] = percentile(stats, 99)
        distribution["p999"] = percentile(stats, 99.9)
        distribution["max"] = max(stats)
        distribution["count"] = len(stats)
        return distribution
    except ValueError:
        return {}
