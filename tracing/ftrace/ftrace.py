import os

from platform import release

class Ftrace(object):
    """
      TODO
        - Change path references to dir or file
    """

    def __init__(self):
        self.tracing_path = "/sys/kernel/debug/tracing/"
        self.current_tracer_path = self.tracing_path + "/current_tracer"
        self.trace_path = self.tracing_path + "/trace"
        self.trace_option_dir = self.tracing_path + "/options"
        self.tracing_on_path = self.tracing_path + "/current_tracer"
        self.tracing_options_path = self.tracing_path + "/trace_options"
        self.snapshot_path = self.tracing_path + "/snapshot"

        self.CONFIG_FTRACE = "CONFIG_FTRACE"
        self.CONFIG_TRACER_SNAPSHOT = "CONFIG_TRACER_SNAPSHOT"
        self.CONFIG_UPROBE_EVENTS = "CONFIG_UPROBE_EVENTS"
        self.CONFIG_KPROBE_EVENTS = "CONFIG_KPROBE_EVENTS"

        self.pre_flight_checks()

    def check_ftrace_option(self, option):
        with open("/boot/config-%s" % (release())) as f:
            if "%s=y" % (option) in f.read():
                return True
            self.exit_with_error("Kernel not compiled with %s!" % (option))
            return False

    def exit_with_error(self, message):
        print message
        exit(1)

    def pre_flight_checks(self):
        self.check_ftrace_option(self.CONFIG_FTRACE)
        if not os.getuid() == 0:
            self.exit_with_error("This program needs to be executed as root")
        if not os.path.isdir(self.tracing_path):
            self.exit_with_error(("Tracing directory %s not found. "
            "Is debugfs mounted?"
            % (self.tracing_path)))
        if self.get_setting(self.current_tracer_path) != "nop":
            self.exit_with_error(("Tracer currently set. "
                "Please echo nop > %s before running this program"
                % (self.current_tracer_path)))

    def get_setting(self, path):
        with open(path) as f:
            setting= f.readline().strip()
        return setting

    def get_trace_snapshot(self):
        self.check_ftrace_option(self.CONFIG_TRACER_SNAPSHOT)
        self.set_value("0", self.snapshot_path)
        self.set_value("1", self.snapshot_path)
        self.set_value("", self.trace_path)
        with open(self.snapshot_path) as f:
            data = f.readlines()
        return data

    def set_format_option(self, option, value):
        self.set_value(value, "%s/%s" % (self.trace_option_dir, option))

    def set_value(self, value, path):
        with open(path, "w") as f:
            f.write(value)
