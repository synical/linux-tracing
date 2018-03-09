import argparse

from tracing.ftrace import function_graph,function

"""
  TODO
    - Latency of function
"""

class FuncTrace(object):

    def __init__(self, pid_filter=False, function_filter=False, stacktrace=False):
        self.ft = function.Function()
        self.stacktrace = stacktrace
        if pid_filter:
            self.ft.generic_filter_pid(pid_filter)
        if function_filter:
            self.ft.filter_function_name(function_filter)
        if stacktrace:
            self.ft.set_format_option("func_stack_trace", "1")

    def cleanup(self):
        if self.stacktrace:
            self.ft.set_format_option("func_stack_trace", "0")
        self.ft.disable_tracing()

    def trace_functions(self):
        self.ft.enable_tracing()
        for line in self.ft.get_trace_snapshot():
            print line,
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    parser.add_argument("-t", "--trace", action="store_true", dest="stacktrace", help="Include stack traces")
    return parser.parse_args()

def main():
    args = parse_args()
    ft = FuncTrace(pid_filter=args.pid, function_filter=args.function, stacktrace=args.stacktrace)
    ft.trace_functions()

if __name__ == "__main__":
    main()
