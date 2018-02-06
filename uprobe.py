#!/usr/bin/env python

import argparse

from platform import release
from time import sleep
from tracing import ftrace

"""
  TODO
    - User level stacktraces
"""

class Uprobe(object):

    def __init__(self, uprobe_event, pid=False, period=0.5, trace=False):
        self.ft = ftrace.Ftrace()
        self.uprobe_event = uprobe_event
        self.pid = pid
        self.period = period
        self.trace = trace

    def cleanup(self):
        if self.trace:
            self.ft.set_format_option("userstacktrace", "0")
            self.ft.set_format_option("display-graph", "0")
            self.ft.set_format_option("sym-userobj", "0")
        self.ft.disable_uprobe_tracing()

    def exit_with_error(self, message):
        print(message)
        exit(1)

    def trace_probe(self):
        try:
            if self.pid:
                self.pid = "common_pid == %s" % (self.pid)
            if self.trace:
                self.ft.set_format_option("userstacktrace", "1")
                self.ft.set_format_option("display-graph", "1")
                self.ft.set_format_option("sym-userobj", "1")
            self.ft.set_uprobe_event(self.uprobe_event)
            self.ft.enable_uprobe_tracing(uprobe_filter=self.pid)
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
    parser.add_argument("-t", "--trace", action="store_true", dest="trace", help="Include user stack traces")
    return parser.parse_args()

def main():
    args = parse_args()
    if int(release()[0]) < 4:
        print "Kernel version must be 4.0 or greater!"
        exit(1)
    up = Uprobe(args.uprobe, pid=args.pid, period=args.sample, trace=args.trace)
    up.trace_probe()

if __name__ == '__main__':
    main()
