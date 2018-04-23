#!/usr/bin/env python

import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import block


class IoRaw(object):

    def __init__(self, device=False, interval=1):
        self.bt = block.Block()
        self.device = device
        self.interval = interval

    def disable_and_exit(self):
        self.bt.disable_tracing()
        exit(0)

    def print_io(self):
        device_io = [l.strip() for l in self.bt.get_trace_snapshot() if self.device in l]
        if device_io:
            print "\n".join(device_io)

    def trace(self):
        self.bt.enable_tracing()
        try:
            print "Raw I/O data for %s" % (self.device)
            while True:
                sleep(float(self.interval))
                self.print_io()
        except KeyboardInterrupt:
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", action="store", dest="device", required=True, help="<MAJ,MIN>")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Collection interval")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    io = IoRaw(device=args.device, interval=args.interval)
    io.trace()

if __name__ == '__main__':
    main()
