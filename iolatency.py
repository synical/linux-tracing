import argparse

from numpy import percentile
from tracing import ftrace

"""
TODO
    * Add arg to filter on reads/writes
"""

class IoLatency(object):

    def __init__(self):
        self.ft = ftrace.Ftrace()
        self.issued = []
        self.completed = []
        self.io_stats = {}
        self.io_times = []

    def compute_io_stats(self):
        self.io_stats["min"] = min(self.io_times)
        self.io_stats["p50"] = percentile(self.io_times, 50)
        self.io_stats["p99"] = percentile(self.io_times, 99)
        self.io_stats["p999"] = percentile(self.io_times, 99.9)
        self.io_stats["max"] = max(self.io_times)
        self.io_stats["count"] = len(self.io_times)

    def disable_and_exit(self, message=False):
        self.ft.disable_block_tracing()
        if message:
            print message
            exit(1)
        exit(0)

    def get_rq_times(self):
        for i in self.issued:
            i_dev = i[4]
            i_offset = i[-4]
            i_time = float(i[2])
            for c in self.completed:
                c_dev = c[4]
                c_offset = c[-4]
                c_time = float(c[2])
                if i_offset == c_offset and i_dev == c_dev:
                    self.io_times.append((c_time - i_time) * 1000)
                    self.completed.remove(c)
                    break

    def print_io_stats(self):
            print "\nIO Latency Statistics (ms):\n"
            for k, v in self.io_stats.iteritems():
                print "%s\t\t%s" % (k, v)

    def trace_io(self, device):
        self.ft.enable_block_tracing()
        for line in self.ft.get_trace_data():
            if "block_rq_issue" in line and device in line:
                self.issued.append(filter(None, line.replace(":", "").split(" ")))
            if "block_rq_complete" in line and device in line:
                self.completed.append(filter(None, line.replace(":", "").split(" ")))

        self.get_rq_times()
        if not self.io_times:
            self.disable_and_exit("No I/O events found.")
        self.compute_io_stats()
        self.print_io_stats()
        self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=True, help="<MAJ,MIN>")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoLatency()
    io.trace_io(args.device)

if __name__ == '__main__':
    main()
