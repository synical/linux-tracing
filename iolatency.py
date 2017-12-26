from numpy import percentile

def compute_io_stats(io_times):
    io_stats = {}
    io_stats["min"] = min(io_times)
    io_stats["p50"] = percentile(io_times, 50)
    io_stats["p99"] = percentile(io_times, 99)
    io_stats["p999"] = percentile(io_times, 99.9)
    io_stats["max"] = max(io_times)
    io_stats["count"] = len(io_times)
    return io_stats

def get_io_times(lines):
    io_times = []
    queued = [filter(None, x.replace(":", "").split(" ")) for x in lines if "block_bio_queue:" in x]
    completed = [filter(None, x.replace(":", "").split(" ")) for x in lines if "block_bio_complete:" in x]
    for i, q in enumerate(queued):
        q_offset = q[6]
        q_time = float(q[2])
        for c in completed:
            c_offset = c[6]
            c_time = float(c[2])
            if q_offset == c_offset:
                io_times.append((c_time - q_time) * 1000)
                completed.remove(c)
                break
    return io_times
    
def print_io_stats(io_stats):
        print "IO Latency Statistics (ms):\n"
        for k, v in io_stats.iteritems():
            print "%s\t\t%s" % (k, v)

def main():
    with open("luks-latency") as f:
        io_times = get_io_times(f.readlines())
    io_stats = compute_io_stats(io_times)
    print_io_stats(io_stats)

if __name__ == '__main__':
    main()
