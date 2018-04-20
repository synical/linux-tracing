import argparse
import re

from collections import Counter
from time import sleep

from tracing import utils
from tracing.ftrace import function

class FunctionCallers(object):

    def __init__(self, pid_filter=False, function_filter=False, show_tasks=False, interval=1):
        self.ft = function.Function()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.show_tasks = show_tasks
        self.interval = interval

        if function_filter:
            self.ft.filter_function_name(function_filter)
        if pid_filter:
            self.ft.generic_filter_pid(pid_filter)

    def cleanup(self):
        self.ft.disable_tracing()
        exit(0)

    def count_callers(self):
        if self.show_tasks:
            callers = [l.strip().split(" ")[0] for l in self.ft.get_trace_snapshot()]
        else:
            callers = [l.strip().split(" ")[-1].strip("<-") for l in self.ft.get_trace_snapshot()]
        caller_counts = Counter(callers).most_common(10)
        for x in caller_counts:
            print "%s: %s" % (x[0], x[1])
        print

    def trace(self):
        self.ft.enable_tracing()
        print "Top 10 callers of %s every %s seconds:\n" % (self.function_filter, self.interval)
        while True:
            try:
                sleep(self.interval)
                self.count_callers()
            except KeyboardInterrupt:
                self.cleanup()
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-t", "--show-tasks", action="store_true", dest="show_tasks", required=False, default=False, help="Display tasks as callers")
    parser.add_argument("-f", "--function", action="store", dest="function", required=True, help="Function to filter")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Sampling interval")
    return parser.parse_args()

def main():
    args = parse_args()
    ft = FunctionCallers(pid_filter=args.pid, function_filter=args.function, show_tasks=args.show_tasks, interval=args.interval)
    ft.trace()

if __name__ == "__main__":
    main()
