from ftrace import Ftrace

class Uprobe(Ftrace):

    """
      TODO
        - Make into a generic probe class for uprobe and kprobe
    """
    def __init__(self, uprobe_filter=None):
        Ftrace.__init__(self)
        self.events_dir = self.tracing_dir + "/events/uprobes/"
        self.events_file = self.tracing_dir + "/uprobe_events"
        self.trace_enable_file = self.events_dir + "/enable"
        self.uprobe_filter = uprobe_filter

        self.required_config_options = [
            "CONFIG_UPROBE_EVENTS"
        ]
        self.pre_flight_checks()

    def disable_tracing(self, message=False):
        self.set_value("0", self.trace_enable_file)
        self.set_value("", self.events_file)
        self.set_value("", self.trace_file)
        if message:
            self.exit_with_error(message)

    def enable_tracing(self):
        if self.uprobe_filter:
            self.set_value(self.uprobe_filter, "%s/filter" % (self.events_dir))
        self.set_value("1", self.trace_enable_file)

    def set_event(self, uprobe_event):
        self.set_value(uprobe_event, self.events_file)
