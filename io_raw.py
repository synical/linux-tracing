#!/usr/bin/env python

import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import block

"""
    TODO
        * Move repeated I/O functions into ftrace modules for DRY
"""

class IoRaw(object):

    def __init__(self, device=False, pid_filter=False, event_filter=False, stacktrace=False, interval=1):
        self.bt = block.Block()
        self.device = device
        self.event_filter = event_filter
        self.interval = interval

        if pid_filter:
            self.bt.set_filter("common_pid == %s" % (pid_filter))
        if event_filter:
            self.event_filter = event_filter.split(",")
        if stacktrace:
            self.bt.set_format_option("stacktrace", "1")

    def disable_and_exit(self):
        self.bt.set_format_option("stacktrace", "0")
        self.bt.disable_tracing()
        exit(0)

    def print_io(self):
        if self.device:
            device_io = [l.strip() for l in self.bt.get_trace_snapshot() if self.device in l]
        else:
            device_io = [l.strip() for l in self.bt.get_trace_snapshot()]
        if device_io:
            print "\n".join(device_io)

    def trace(self):
        self.bt.enable_tracing(events=self.event_filter)
        self.bt.set_format_option("stacktrace", "1")
        try:
            while True:
                print "\nRaw I/O data for last %s seconds\n" % (self.interval)
                sleep(float(self.interval))
                self.print_io()
        except KeyboardInterrupt:
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=False, help="<MAJ,MIN>")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Collection interval")
    parser.add_argument("-p", "--pid", action="store", dest="pid", default=False, help="Pid to filter")
    parser.add_argument("-f", "--filter", action="store", dest="event_filter", default=False, help="Comma separated I/O event filter")
    parser.add_argument("-s", "--stacktrace", action="store_true", dest="stacktrace", default=False, help="Capture stacktraces")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoRaw(device=args.device, pid_filter=args.pid, event_filter=args.event_filter, stacktrace=args.stacktrace, interval=args.interval)
    io.trace()

if __name__ == '__main__':
    main()
