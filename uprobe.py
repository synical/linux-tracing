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

    def __init__(self, uprobe_event):
        self.ft = ftrace.Ftrace()
        self.uprobe_event = uprobe_event

    def exit_with_error(self, message):
        print(message)
        exit(1)

    def trace_entry(self, pid=None, period=1):
        try:
            if pid:
                pid = "common_pid == %s" % (pid)
            self.ft.set_uprobe_event(self.uprobe_event)
            self.ft.enable_uprobe_tracing(uprobe_filter=pid)
        except IOError:
            self.exit_with_error("Invalid uprobe '%s'" % (self.uprobe_event))
        sleep(float(period))
        for line in self.ft.get_trace_snapshot():
            if line[0] != "#":
                print line,
        self.ft.disable_uprobe_tracing()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uprobe", action="store", dest="uprobe", required=True, help="uprobe entry point")
    parser.add_argument("-p", "--pid", action="store", dest="pid", help="pid to filter on")
    parser.add_argument("-s", "--sample", action="store", dest="sample", default=1, help="Seconds to sample for")
    return parser.parse_args()

def main():
    args = parse_args()
    if int(release()[0]) < 4:
        print "Kernel version must be 4.0 or greater!"
        exit(1)
    up = Uprobe(args.uprobe)
    up.trace_entry(pid=args.pid, period=args.sample)

if __name__ == '__main__':
    main()
