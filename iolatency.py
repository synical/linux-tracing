import argparse

from numpy import percentile
from tracing import ftrace

"""
TODO
    * Add arg to filter on reads/writes
"""

def compute_io_stats(io_times):
    io_stats = {}
    io_stats["min"] = min(io_times)
    io_stats["p50"] = percentile(io_times, 50)
    io_stats["p99"] = percentile(io_times, 99)
    io_stats["p999"] = percentile(io_times, 99.9)
    io_stats["max"] = max(io_times)
    io_stats["count"] = len(io_times)
    return io_stats

def disable_and_exit(ft, message=False):
    ft.disable_block_tracing()
    if message:
        print message
        exit(1)
    exit(0)

def get_rq_times(issued, completed):
    io_times = []
    for i in issued:
        i_dev = i[4]
        i_offset = i[-4]
        i_time = float(i[2])
        for c in completed:
            c_dev = c[4]
            c_offset = c[-4]
            c_time = float(c[2])
            if i_offset == c_offset and i_dev == c_dev:
                io_times.append((c_time - i_time) * 1000)
                completed.remove(c)
                break
    return io_times

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=True, help="<MAJ,MIN>")
    args = parser.parse_args()
    return args

def print_io_stats(io_stats):
        print "\nIO Latency Statistics (ms):\n"
        for k, v in io_stats.iteritems():
            print "%s\t\t%s" % (k, v)

def trace_io(device):
    ft = ftrace.Ftrace()
    ft.enable_block_tracing()
    issued = []
    completed = []

    for line in ft.get_trace_data():
        if "block_rq_issue" in line and device in line:
            issued.append(filter(None, line.replace(":", "").split(" ")))
        if "block_rq_complete" in line and device in line:
            completed.append(filter(None, line.replace(":", "").split(" ")))

    io_times = get_rq_times(issued, completed)
    if not io_times:
        disable_and_exit(ft, "No I/O events found.")
    print_io_stats(compute_io_stats(io_times))
    disable_and_exit(ft)

def main():
    args = parse_args()
    trace_io(args.device)

if __name__ == '__main__':
    main()
