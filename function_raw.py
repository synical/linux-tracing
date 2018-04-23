import argparse

from time import sleep

from tracing import utils
from tracing.ftrace import function

class FunctionRaw(object):

    def __init__(self, pid_filter=False, function_filter=False, stacktrace=False, interval=1):
        self.ft = function.Function()
        self.pid_filter = pid_filter
        self.function_filter = function_filter
        self.stacktrace = stacktrace
        self.interval = interval

        if function_filter:
            self.ft.filter_function_name(function_filter)
        if pid_filter:
            self.ft.generic_filter_pid(pid_filter)
        if stacktrace:
            self.ft.set_format_option("func_stack_trace", "1")

    def cleanup(self):
        self.ft.set_format_option("func_stack_trace", "0")
        self.ft.disable_tracing()
        exit(0)

    def print_raw_function_trace(self):
        for line in self.ft.get_trace_snapshot():
            print line,

    def trace(self):
        self.ft.enable_tracing()
        while True:
            try:
                self.print_raw_function_trace()
                sleep(self.interval)
            except KeyboardInterrupt:
                self.cleanup()
        self.cleanup()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, default=False, help="Pid to filter")
    parser.add_argument("-f", "--function", action="store", dest="function", required=False, default=False, help="Function to filter")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Sampling interval")
    parser.add_argument("-s", "--stacktrace", action="store_true", dest="stacktrace", default=False, help="Capture stacktraces")
    return parser.parse_args()

def main():
    args = parse_args()
    fr = FunctionRaw(pid_filter=args.pid, function_filter=args.function, stacktrace=args.stacktrace, interval=args.interval)
    fr.trace()

if __name__ == "__main__":
    main()
