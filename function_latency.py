import argparse
import re

from collections import Counter
from time import sleep

from tracing import utils
from tracing.ftrace import function_graph

class FunctionLatency(object):

    def __init__(self, pid_filter=False, function_filter=False, interval=5):
        self.fg = function_graph.FunctionGraph()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.interval = interval

        if function_filter:
            self.fg.filter_function_name(function_filter)
        if pid_filter:
            self.fg.generic_filter_pid(pid_filter)

    def cleanup(self):
        self.fg.disable_tracing()
        exit(0)

    def parse_latencies(self):
        try:
            function_latencies = filter(None, [l.split("|")[0].strip() for l in self.fg.get_trace_snapshot() if self.function_filter in l])
            function_latencies = [re.findall(r"[0-9]+\.[0-9]+", f) for f in function_latencies]
            function_latencies = [float(m[0]) for m in function_latencies if len(m) > 0]
        except IndexError:
            print function_latencies
            raise
        function_latencies.sort(reverse=True)
        return function_latencies

    def trace_latency(self):
        function_latencies = self.parse_latencies()
        self.latency_distribution = []
        print "\nLatency distribution of '%s'\n" % (self.function_filter)
        for k, v in utils.compute_distribution(function_latencies).iteritems():
            print "%s\t\t%0.2f" % (k, v)

    def trace(self):
        self.fg.enable_tracing()
        while True:
            try:
                sleep(self.interval)
                self.trace_latency()
            except KeyboardInterrupt:
                self.cleanup()
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=True, default=False, help="Function to filter")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=5, help="Sampling interval")
    return parser.parse_args()

def main():
    args = parse_args()
    fl = FunctionLatency(pid_filter=args.pid, function_filter=args.function, interval=float(args.interval))
    fl.trace()

if __name__ == "__main__":
    main()
