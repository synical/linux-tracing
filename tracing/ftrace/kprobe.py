from ftrace import Ftrace

class Kprobe(Ftrace):

    """
      TODO
        - Make into a generic probe class for uprobe and kprobe
    """
    def __init__(self, kprobe_filter=None):
        Ftrace.__init__(self)
        self.events_dir = self.tracing_dir + "/events/kprobes/"
        self.events_file = self.tracing_dir + "/kprobe_events"
        self.trace_enable_file = self.events_dir + "/enable"
        self.kprobe_filter = kprobe_filter

    def disable_tracing(self, message=False):
        self.set_value("0", self.trace_enable_file)
        self.set_value("", self.events_file)
        self.set_value("", self.trace_file)
        if message:
            self.exit_with_error(message)

    def enable_tracing(self):
        if self.kprobe_filter:
            self.set_value(self.kprobe_filter, "%s/filter" % (self.events_dir))
        self.set_value("1", self.trace_enable_file)

    def set_event(self, kprobe_event):
        self.check_ftrace_option(self.CONFIG_KPROBE_EVENTS)
        self.set_value(kprobe_event, self.events_file)
