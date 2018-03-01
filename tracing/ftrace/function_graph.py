from ftrace import Ftrace

class FunctionGraph(Ftrace):

    def __init__(self):
        Ftrace.__init__(self)

    def disable_tracing(self):
        pass

    def enable_tracing(self):
        pass
