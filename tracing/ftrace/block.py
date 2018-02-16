from ftrace import Ftrace

class Block(Ftrace):

    def __init__(self):
        Ftrace.__init__(self)
        self.events_path = self.tracing_path + "/events/block"
        self.trace_enable_path = self.events_path + "/enable"

    def disable_tracing(self, message=False):
        self.set_value("0", self.trace_enable_path)
        if message:
            Ftrace.exit_with_error(message)

    def enable_tracing(self, events=None):
        self.set_format_option("irq-info", "0")
        if events:
            for e in events:
                self.set_value("1", "%s/%s/enable" % (self.events_path, e))
        else:
            self.set_value("1", self.trace_enable_path)

