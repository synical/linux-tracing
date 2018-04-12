import argparse
import re

from collections import Counter
from time import sleep

from tracing import utils
from tracing.ftrace import function_graph,function

"""
  TODO
    - Latency histogram
"""

class FuncTrace(object):

    def __init__(self, pid_filter=False, function_filter=False, stacktrace=False, count=False, latency=False, interval=1):
        self.ft = function.Function()
        self.fg = function_graph.FunctionGraph()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.stacktrace = stacktrace
        self.count = count
        self.latency = latency
        self.interval = interval

        if function_filter:
            self.ft.filter_function_name(function_filter)
        if pid_filter:
            self.ft.generic_filter_pid(pid_filter)
        if latency:
            self.ft.set_format_option("funcgraph-cpu", "0")
        if stacktrace:
            self.ft.set_format_option("func_stack_trace", "1")

    def cleanup(self):
        self.ft.set_format_option("func_stack_trace", "0")
        self.ft.set_format_option("funcgraph-cpu", "1")
        self.ft.disable_tracing()
        self.fg.disable_tracing()
        exit(0)

    def count_callers(self):
        self.ft.enable_tracing()
        callers = [l.strip().split(" ")[-1].strip("<-") for l in self.ft.get_trace_snapshot()]
        caller_counts = Counter(callers).most_common(10)
        print "Top 10 callers of %s:\n" % (self.function_filter)
        for x in caller_counts:
            print "%s: %s" % (x[0], x[1])

    def parse_latencies(self):
        function_latencies = filter(None, [l.split("|")[0].strip() for l in self.fg.get_trace_snapshot() if self.function_filter in l])
        function_latencies = [float(re.findall(r"[0-9]+\.[0-9]+", f)[0]) for f in function_latencies]
        function_latencies.sort(reverse=True)
        return function_latencies

    def raw_function_trace(self):
        self.ft.enable_tracing()
        for line in self.ft.get_trace_snapshot():
            print line,

    def trace_latency(self):
        self.fg.enable_tracing()
        function_latencies = self.parse_latencies()
        self.latency_distribution = []
        print "\nLatency distribution of '%s'\n" % (self.function_filter)
        for k, v in utils.compute_distribution(function_latencies).iteritems():
            print "%s\t\t%0.2f" % (k, v)

    def trace_functions(self):
        if self.latency:
            trace_function = self.trace_latency
        elif self.count:
            trace_function = self.count_callers
        else:
            trace_function = self.raw_function_trace
        while True:
            try:
                sleep(self.interval)
                trace_function()
            except KeyboardInterrupt:
                self.cleanup()
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    parser.add_argument("-t", "--trace", action="store_true", dest="stacktrace", help="Include stack traces")
    parser.add_argument("-c", "--count", action="store_true", dest="count", help="Output a count of the top callers")
    parser.add_argument("-l", "--latency", action="store_true", dest="latency", help="Get latency info on function passed with -f/--function")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Sampling interval")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.count and not args.function:
        print "Cannot use count arg without function arg!"
        exit(1)
    if args.latency and not args.function:
        print "Cannot use latency arg without function arg!"
        exit(1)
    ft = FuncTrace(pid_filter=args.pid, function_filter=args.function, stacktrace=args.stacktrace, count=args.count, latency=args.latency, interval=args.interval)
    ft.trace_functions()

if __name__ == "__main__":
    main()
