import argparse

from tracing.ftrace import function_graph,function

class FuncTrace(object):

    def __init__(self, pid_filter=False):
        self.ft = function.Function()
        self.pid_filter = pid_filter

    def trace_functions(self):
        if self.pid_filter:
            self.ft.generic_filter_pid(self.pid_filter)
        self.ft.enable_tracing()
        for line in self.ft.get_trace_snapshot():
            print line,
        self.ft.disable_tracing()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    return parser.parse_args()

def main():
    args = parse_args()
    ft = FuncTrace(pid_filter=args.pid)
    ft.trace_functions()

if __name__ == "__main__":
    main()
