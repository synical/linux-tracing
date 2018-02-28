#!/usr/bin/env python

import argparse

from platform import release
from time import sleep
from tracing.ftrace import uprobe

"""
Script for interacting with ftrace uprobes
    Examples:
        Get size of malloc requests
        $ sudo python uprobe.py -u "p:malloc_entry /usr/lib64/libc.so.6:0x907a0 mem_requested=%di:u64" -p 18866
        a.out-18866 [001] d... 156741.233725: malloc_entry: (0x7fe7a77af7a0) mem_requested=1
        ...
"""

class UprobeTracer(object):

    def __init__(self, uprobe_event, pid_filter=False, period=0.5, stacktrace=False):
        self.pid_filter = pid_filter
        if pid_filter:
            self.pid_filter = "common_pid == %s" % (self.pid_filter)
        self.ft = uprobe.Uprobe(uprobe_filter=self.pid_filter)
        self.uprobe_event = uprobe_event
        self.period = period
        self.stacktrace = stacktrace

    def cleanup(self):
        if self.stacktrace:
            self.ft.set_format_option("userstacktrace", "0")
            self.ft.set_format_option("display-graph", "0")
            self.ft.set_format_option("sym-userobj", "0")
        self.ft.disable_tracing()

    def exit_with_error(self, message):
        print(message)
        exit(1)

    def trace_probe(self):
        try:
            if self.stacktrace:
                self.ft.set_format_option("userstacktrace", "1")
                self.ft.set_format_option("display-graph", "1")
                self.ft.set_format_option("sym-userobj", "1")
            self.ft.set_event(self.uprobe_event)
            self.ft.enable_tracing()
        except IOError:
            self.exit_with_error("Invalid uprobe '%s'" % (self.uprobe_event))
        sleep(float(self.period))
        for line in self.ft.get_trace_snapshot():
            if line[0] != "#":
                print line,
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uprobe", action="store", dest="uprobe", required=True, help="uprobe entry point")
    parser.add_argument("-p", "--pid", action="store", dest="pid", help="pid to filter on")
    parser.add_argument("-s", "--sample", action="store", dest="sample", default=1, help="Seconds to sample for")
    parser.add_argument("-t", "--trace", action="store_true", dest="stacktrace", help="Include user stack traces")
    return parser.parse_args()

def main():
    args = parse_args()
    if int(release()[0]) < 4:
        print "Kernel version must be 4.0 or greater!"
        exit(1)
    up = UprobeTracer(args.uprobe, pid_filter=args.pid, period=args.sample, stacktrace=args.stacktrace)
    up.trace_probe()

if __name__ == '__main__':
    main()
