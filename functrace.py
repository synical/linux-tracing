import argparse

from collections import Counter

from tracing.ftrace import function_graph,function

"""
  TODO
    - Latency histogram
    - Sampling period
"""

class FuncTrace(object):

    def __init__(self, pid_filter=False, function_filter=False, stacktrace=False, count=False, latency=False):
        self.ft = function.Function()
        self.fg = function_graph.FunctionGraph()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.stacktrace = stacktrace
        self.count = count
        self.latency = latency
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

    def count_callers(self):
        callers = [l.strip().split(" ")[-1].strip("<-") for l in self.ft.get_trace_snapshot()]
        caller_counts = Counter(callers).most_common()
        print "Top 10 callers of %s:\n" % (self.function_filter)
        for x in caller_counts[:10]:
            print "%s: %s" % (x[0], x[1])

    def trace_latency(self):
        self.fg.enable_tracing()
        function_latencies = filter(None, [l.split("|")[0].strip() for l in self.fg.get_trace_snapshot() if self.function_filter in l])
        function_latencies.sort(reverse=True)
        print "Top 10 slowest '%s' calls\n\n%s" % (self.function_filter, "\n".join(function_latencies[:10]))

    def trace_functions(self):
        if self.latency:
            self.trace_latency()
        else:
            self.ft.enable_tracing()
            if self.count:
                self.count_callers()
            else:
                for line in self.ft.get_trace_snapshot():
                    print line,
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    parser.add_argument("-t", "--trace", action="store_true", dest="stacktrace", help="Include stack traces")
    parser.add_argument("-c", "--count", action="store_true", dest="count", help="Output a count of the top callers")
    parser.add_argument("-l", "--latency", action="store_true", dest="latency", help="Get latency info on function passed with -f/--function")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.count and not args.function:
        print "Cannot use count arg without function arg!"
        exit(1)
    if args.latency and not args.function:
        print "Cannot use latency arg without function arg!"
        exit(1)
    ft = FuncTrace(pid_filter=args.pid, function_filter=args.function, stacktrace=args.stacktrace, count=args.count, latency=args.latency)
    ft.trace_functions()

if __name__ == "__main__":
    main()
