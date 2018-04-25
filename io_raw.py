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

    def __init__(self, device=False, pid_filter=False, interval=1):
        self.bt = block.Block()
        self.device = device
        self.interval = interval

        if pid_filter:
            self.bt.set_filter("common_pid == %s" % (pid_filter))

    def disable_and_exit(self):
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
        self.bt.enable_tracing()
        try:
            while True:
                print "Raw I/O data stats for last %s seconds" % (self.interval)
                sleep(float(self.interval))
                self.print_io()
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
    io = IoRaw(device=args.device, pid_filter=args.pid, interval=args.interval)
    io.trace()

if __name__ == '__main__':
    main()
