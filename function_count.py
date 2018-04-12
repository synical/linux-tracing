import argparse

from collections import Counter
from time import sleep

from tracing.ftrace import function

class FunctionCount(object):

    def __init__(self, pid_filter=False, function_filter=False, interval=1.0, limit=10):
        self.ft = function.Function()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.interval = interval
        self.limit = limit

        if function_filter:
            self.ft.filter_function_name(function_filter)
        if pid_filter:
            self.ft.generic_filter_pid(pid_filter)

    def cleanup(self):
        self.ft.disable_tracing()
        exit(0)

    def count_functions(self):
        functions = [l.split(":")[-1].split(" ")[1] for l in self.ft.get_trace_snapshot()]
        function_counts = Counter(functions).most_common(self.limit)
        for f in function_counts:
            print "%s (%s)" % (f[0], f[1])
        print

    def trace(self):
        print "Counting function calls every %s seconds\n" % (self.interval)
        self.ft.enable_tracing()
        while True:
            try:
                sleep(self.interval)
                self.count_functions()
            except KeyboardInterrupt:
                self.cleanup()
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1.0, help="Sampling interval")
    parser.add_argument("-l", "--limit", action="store", dest="limit", default=10, help="Number of functions to show counts for")
    return parser.parse_args()

def main():
    args = parse_args()
    fc = FunctionCount(pid_filter=args.pid, function_filter=args.function, interval=float(args.interval), limit=int(args.limit))
    fc.trace()

if __name__ == "__main__":
    main()
