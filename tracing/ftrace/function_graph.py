from function import Function

class FunctionGraph(Function):

    def __init__(self):
        Function.__init__(self)
        self.tracer_name = "function_graph"

    def disable_tracing(self):
        Function.disable_tracing(self)

    def enable_tracing(self):
        self.set_value(self.tracer_name, self.current_tracer_file)
