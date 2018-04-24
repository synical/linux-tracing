#!/usr/bin/env python

import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import block

"""
TODO
    * Optimise (cannot handle high I/O rate)
"""

class IoLatency(object):

    def __init__(self, device=False, queue=False, bio=False, operation=False, interval=1, histogram=False):
        self.ft = block.Block()
        self.device = device
        self.histogram = histogram
        self.operation = operation
        self.interval = interval
        self.issued = []
        self.completed = []
        self.io_times = []
        if bio:
            self.io_start = "block_bio_queue"
            self.io_end = "block_bio_complete"
        else:
            if queue:
                self.io_start = "block_rq_insert"
            else:
                self.io_start = "block_rq_issue"
            self.io_end = "block_rq_complete"

    def clear_io_stats(self):
        self.issued = []
        self.completed = []
        self.io_times = []

    def compute_io_stats(self):
        for line in self.ft.get_trace_snapshot():
            if self.io_start in line and self.device in line:
                split_line = self.parse_line(line)
                if not self.operation:
                    self.issued.append(split_line)
                    continue
                if self.operation in split_line[5]:
                    self.issued.append(split_line)
            if self.io_end in line and self.device in line:
                split_line = self.parse_line(line)
                if not self.operation:
                    self.completed.append(split_line)
                    continue
                if self.operation in split_line[5]:
                    self.completed.append(split_line)

    def disable_and_exit(self, message=False):
        self.ft.disable_tracing()
        self.ft.set_format_option("irq-info", "1")
        if message:
            print message
            exit(1)
        exit(0)

    def get_rq_times(self):
        for i in self.issued:
            i_dev = i[2]
            i_offset = i[6]
            i_time = float(i[0])
            for c in self.completed:
                c_dev = c[2]
                c_offset = c[5]
                c_time = float(c[0])
                if i_offset == c_offset and i_dev == c_dev:
                    self.io_times.append((c_time - i_time) * 1000)
                    self.completed.remove(c)
                    break

    def parse_line(self, line):
        line = filter(None, line.replace(":", "").split(" "))
        for i, x in enumerate(line):
            if x.startswith("[") and x.endswith("]"):
                return line[i+1:-1]
        return line

    def print_io_stats(self):
            self.get_rq_times()
            if self.histogram:
                utils.compute_histogram(self.io_times)
            else:
                print "\nIO Latency Statistics (ms):\n"
                utils.print_distribution(self.io_times)

    def trace(self):
        self.ft.set_format_option("irq-info", "0")
        self.ft.enable_tracing(events=[self.io_start, self.io_end])
        try:
            print "Collecting trace data. Ctrl-C to stop."
            while True:
                sleep(float(self.interval))
                self.compute_io_stats()
                self.print_io_stats()
                self.clear_io_stats()
        except KeyboardInterrupt:
            self.compute_io_stats()
            self.print_io_stats()
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=True, help="<MAJ,MIN>")
    parser.add_argument("-o", "--operation", action="store", dest="operation", help="<W,R>")
    parser.add_argument("-q", "--queue", action="store_true", dest="queue", help="Use block_rq_insert event as start of I/O")
    parser.add_argument("-b", "--bio", action="store_true", dest="bio", help="Trace bio operations (useful for device mappers)")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Collection interval")
    parser.add_argument("--histogram", action="store_true", dest="histogram", default=False, help="Histogram output")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoLatency(device=args.device, queue=args.queue, bio=args.bio, operation=args.operation, interval=args.interval, histogram=args.histogram)
    io.trace()

if __name__ == '__main__':
    main()
