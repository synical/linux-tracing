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

def compute_histogram(stats):
    counts = {x: stats.count(x) for x in set(stats)}
    lowest = min(stats)
    highest = max(stats)
    
    i=0
    while True:
        if i == 0:
            print "0\t->\t1\t0"
            i=2
        first = i
        second = ((i*2)-1)
        num_hits = sum([counts[k] for k in counts.keys() if k >= first and k <= second])
        print "%d\t->\t%d\t%d" % (first, second, num_hits)
        i*=2
        if i > highest:
            break
