#!/usr/bin/env python

import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import block

class IoSize(object):

    def __init__(self, device=False, pid_filter=False, interval=1):
        self.bt = block.Block()
        self.device = device
        self.interval = interval

        if pid_filter:
            self.bt.set_filter("common_pid == %s" % (pid_filter))

    def disable_and_exit(self):
        self.bt.set_format_option("blk_classic", "0")
        self.bt.disable_tracing()
        exit(0)

    def print_io_size(self):
        if self.device:
            io_sizes = [int(l.split(" ")[3]) for l in self.bt.get_trace_snapshot() if self.device in l]
        else:
            io_sizes = [int(l.split(" ")[3]) for l in self.bt.get_trace_snapshot()]
        if io_sizes:
            utils.print_distribution(io_sizes)

    def trace(self):
        self.bt.set_format_option("blk_classic", "1")
        self.bt.enable_tracing(events=["block_rq_issue"])
        try:
            while True:
                sleep(float(self.interval))
                print "I/O stats for last %s seconds\n" % (self.interval)
                self.print_io_size()
        except KeyboardInterrupt:
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=False, help="<MAJ,MIN>")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Collection interval")
    parser.add_argument("-p", "--pid", action="store", dest="pid", default=False, help="Pid to filter")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoSize(device=args.device, pid_filter=args.pid, interval=args.interval)
    io.trace()

if __name__ == '__main__':
    main()
