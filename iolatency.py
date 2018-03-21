#!/usr/bin/env python

import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import block

"""
TODO
    * Add histogram output support
    * Print results on Ctrl-C
"""

# https://elixir.free-electrons.com/linux/v3.14/source/include/trace/events/block.h
# http://elixir.free-electrons.com/linux/v3.14/source/include/linux/blk_types.h
# http://elixir.free-electrons.com/linux/v3.14/source/kernel/trace/blktrace.c#L1803

class IoLatency(object):

    def __init__(self, queue=False, bio=False):
        self.ft = block.Block()
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

    def disable_and_exit(self, message=False):
        self.ft.disable_tracing()
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
                try:
                    c_time = float(c[2])
                except ValueError:
                    print "Problem converting to float. Row was %s" % (c)
                    self.disable_and_exit()
                if i_offset == c_offset and i_dev == c_dev:
                    self.io_times.append((c_time - i_time) * 1000)
                    self.completed.remove(c)
                    break

    def print_io_stats(self):
            self.get_rq_times()
            io_stats = utils.compute_distribution(self.io_times)
            print "\nIO Latency Statistics (ms):\n"
            for k, v in io_stats.iteritems():
                print "%s\t\t%0.2f" % (k, v)

    def trace_io(self, device, operation=False, interval=10):
        self.ft.enable_tracing(events=[self.io_start, self.io_end])
        try:
            print "Collecting trace data. Ctrl-C to stop."
            while True:
                sleep(float(interval))

                for line in self.ft.get_trace_snapshot():
                    if self.io_start in line and device in line:
                        split_line = filter(None, line.replace(":", "").split(" "))
                        split_line[0].replace(" ", "")
                        if not operation:
                            self.issued.append(split_line)
                            continue
                        if operation in split_line[5]:
                            self.issued.append(split_line)
                    if self.io_end in line and device in line:
                        split_line = filter(None, line.replace(":", "").split(" "))
                        if not operation:
                            self.completed.append(split_line)
                            continue
                        if operation in split_line[5]:
                            self.completed.append(split_line)

                self.print_io_stats()
                self.clear_io_stats()
        except KeyboardInterrupt:
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=True, help="<MAJ,MIN>")
    parser.add_argument("-o", "--operation", action="store", dest="operation", required=False, help="<W,R>")
    parser.add_argument("-q", "--queue", action="store_true", dest="queue", required=False, help="Use block_rq_insert event as start of I/O")
    parser.add_argument("-b", "--bio", action="store_true", dest="bio", required=False, help="Trace bio operations (useful for device mappers)")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, required=False, help="Collection interval")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoLatency(queue=args.queue, bio=args.bio)
    io.trace_io(args.device, operation=args.operation, interval=args.interval)

if __name__ == '__main__':
    main()
