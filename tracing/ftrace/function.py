from ftrace import Ftrace

class Function(Ftrace):

    def __init__(self):
        Ftrace.__init__(self)
        self.function_available_file = self.tracing_dir + "available_filter_functions"
        self.function_filter_file = self.tracing_dir + "set_ftrace_filter"
        self.tracer_name = "function"

        self.CONFIG_DYNAMIC_FTRACE = "CONFIG_DYNAMIC_FTRACE"

    def disable_tracing(self):
        self.generic_disable_tracing()

    def enable_tracing(self):
        self.set_value(self.tracer_name, self.current_tracer_file)

    def filter_function_name(self, function):
        if self.check_function_available(function):
            self.set_value(self.function_filter_file, function)
        else:
            self.disable_tracing()
            self.exit_with_error("Function %s not available to trace!" % (function))

    def check_function_available(self, function):
        with open(self.function_available_file, "r") as f:
            if function in f.readlines():
                return True
        return False
