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

def compute_histogram(stats, unit="ms"):
    counts = {x: stats.count(x) for x in set(stats)}
    stats_len = len(stats)
    lowest = min(stats)
    highest = max(stats)
    bar_length = float(10)
    
    print "Value(%s)\t\tCount\t\tDistribution" % (unit)
    if lowest == 0:
        print "0\t->\t1\t0"
        i = 1
    else:
        i = lowest

    while True:
        first = i
        if first == 1:
            second = 2
        else:
            second = ((i*2)-1)
        num_hits = sum([counts[k] for k in counts.keys() if k >= first and k <= second])
        frequency = (float(num_hits)/float(stats_len) * 100) / bar_length
        bar = "#" * int(frequency)
        print "%d\t->\t%d\t%d\t\t%s" % (first, second, num_hits, bar)
        i*=2
        if i > highest:
            break
