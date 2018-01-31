#!/usr/bin/env python

import argparse

from platform import release
from time import sleep
from tracing import ftrace

"""
  TODO
    - Interval based output
    - Filter on pid
    - User level stacktraces
    - Return value tracing
"""

class Uprobe(object):

    def __init__(self, uprobe_event):
        self.ft = ftrace.Ftrace()
        self.uprobe_event = uprobe_event

    def exit_with_error(self, message):
        print(message)
        exit(1)

    def parse_uprobe(self):
        error_message = "Invalid uprobe, must be of format 'p:<name> <file>:<addr> <args...>'!" 
        try:
            uprobe_string = self.uprobe_event.split(" ")
            uprobe_name = uprobe_string[0].split(":")
            uprobe_entry = uprobe_string[1].split(":")
        except IndexError:
            self.exit_with_error(error_message)
        if self.uprobe_event[0] != "p" or len(uprobe_name) != 2 or len(uprobe_entry) !=2:
            self.exit_with_error(error_message)

    def trace_entry(self):
        self.parse_uprobe()
        self.ft.set_uprobe_event(self.uprobe_event)
        self.ft.enable_uprobe_tracing()
        for line in self.ft.get_trace_snapshot():
            if line[0] != "#":
                print line,
        self.ft.disable_uprobe_tracing()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uprobe", action="store", dest="uprobe", required=True, help="uprobe entry point")
    return parser.parse_args()

def main():
    args = parse_args()
    if int(release()[0]) < 4:
        print "Kernel version must be 4.0 or greater!"
        exit(1)
    up = Uprobe(args.uprobe)
    up.trace_entry()

if __name__ == '__main__':
    main()
