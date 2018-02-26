#!/usr/bin/env python

import argparse

from platform import release
from time import sleep
from tracing.ftrace import kprobe

"""
Script for interacting with ftrace kprobes
    Examples:
        Get size of malloc requests
        $ sudo python kprobe.py -k "p:spin_lock _raw_spin_lock"
        python-30946 [001]  1065763.652811: spin_lock: (_raw_spin_lock+0x0/0x20)
        ...
"""

class KprobeTracer(object):

    def __init__(self, kprobe_event, pid_filter=False, period=0.5, stacktrace=False):
        self.pid_filter = pid_filter
        if pid_filter:
            self.pid_filter = "common_pid == %s" % (self.pid_filter)
        self.ft = kprobe.Kprobe(kprobe_filter=self.pid_filter)
        self.kprobe_event = kprobe_event
        self.period = period
        self.stacktrace = stacktrace

    def cleanup(self):
        if self.stacktrace:
            self.ft.set_format_option("stacktrace", "0")
            self.ft.set_format_option("display-graph", "0")
        self.ft.disable_tracing()

    def exit_with_error(self, message):
        print(message)
        exit(1)

    def trace_probe(self):
        try:
            if self.stacktrace:
                self.ft.set_format_option("stacktrace", "1")
                self.ft.set_format_option("display-graph", "1")
            self.ft.set_event(self.kprobe_event)
            self.ft.enable_tracing()
        except IOError:
            self.exit_with_error("Invalid kprobe '%s'" % (self.kprobe_event))
        sleep(float(self.period))
        for line in self.ft.get_trace_snapshot():
            if line[0] != "#":
                print line,
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kprobe", action="store", dest="kprobe", required=True, help="kprobe entry point")
    parser.add_argument("-p", "--pid", action="store", dest="pid", help="pid to filter on")
    parser.add_argument("-s", "--sample", action="store", dest="sample", default=1, help="Seconds to sample for")
    parser.add_argument("-t", "--trace", action="store_true", dest="stacktrace", help="Include stack traces")
    return parser.parse_args()

def main():
    args = parse_args()
    kp = KprobeTracer(args.kprobe, pid_filter=args.pid, period=args.sample, stacktrace=args.stacktrace)
    kp.trace_probe()

if __name__ == '__main__':
    main()
