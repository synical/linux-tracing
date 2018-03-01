from ftrace import Ftrace

class Function(Ftrace):

    def __init__(self):
        Ftrace.__init__(self)
        self.tracer_name = "function"

    def disable_tracing(self):
        self.generic_disable_tracing()

    def enable_tracing(self):
        self.set_value(self.tracer_name, self.current_tracer_file)
