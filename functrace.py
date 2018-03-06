import argparse

from tracing.ftrace import function_graph,function

"""
  TODO
    - Filter on function
    - Latency of function
    - Stack traces of function
"""

class FuncTrace(object):

    def __init__(self, pid_filter=False, function_filter=False):
        self.ft = function.Function()
        self.pid_filter = pid_filter
        self.function_filter = function_filter

    def trace_functions(self):
        if self.pid_filter:
            self.ft.generic_filter_pid(self.pid_filter)
        if self.function_filter:
            self.ft.filter_function_name(self.function_filter)
        self.ft.enable_tracing()
        for line in self.ft.get_trace_snapshot():
            print line,
        self.ft.disable_tracing()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    return parser.parse_args()

def main():
    args = parse_args()
    ft = FuncTrace(pid_filter=args.pid, function_filter=args.function)
    ft.trace_functions()

if __name__ == "__main__":
    main()
