from numpy import percentile,mean

def print_distribution(stats):
    try:
        distribution = {}
        distribution["min"] = min(stats)
        distribution["p50"] = percentile(stats, 50)
        distribution["p99"] = percentile(stats, 99)
        distribution["p999"] = percentile(stats, 99.9)
        distribution["max"] = max(stats)
        distribution["count"] = len(stats)
        distribution["mean"] = mean(stats)
        for k, v in distribution.iteritems():
            print "%s\t\t%0.2f" % (k, v)
        print
    except ValueError:
        print

def compute_histogram(stats, unit="ms"):
    print "\nValue(%s)\t\tCount\t\tDistribution" % (unit)
    try:
        stats = [int(x) for x in stats]
        counts = {x: stats.count(x) for x in set(stats) if x > 0}
        if not len(counts):
            return
        stats_len = len(stats)
        lowest = min(stats)
        highest = max(stats)
        bar_length = float(10)
    except ValueError:
        return
    
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
