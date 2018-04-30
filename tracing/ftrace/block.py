from ftrace import Ftrace

class Block(Ftrace):

    def __init__(self):
        Ftrace.__init__(self)
        self.events_dir = self.tracing_dir + "/events/block"
        self.filter_file = self.tracing_dir + "/events/block/filter"
        self.trace_enable_file = self.events_dir + "/enable"

    def disable_tracing(self, message=False):
        self.set_value("0", self.trace_enable_file)
        self.set_value("0", self.filter_file)
        self.generic_disable_tracing()
        if message:
            self.exit_with_error(message)

    def enable_tracing(self, events=None):
        if events:
            for e in events:
                self.set_value("1", "%s/%s/enable" % (self.events_dir, e))
        else:
            self.set_value("1", self.trace_enable_file)

    def set_filter(self, block_filter):
        self.set_value(block_filter, self.filter_file)
