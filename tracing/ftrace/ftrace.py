import os

from platform import release

"""
  TODO
    - Do config checks per module
"""

class Ftrace(object):

    def __init__(self):
        self.tracing_dir = "/sys/kernel/debug/tracing/"
        self.current_tracer_file = self.tracing_dir + "/current_tracer"
        self.trace_file = self.tracing_dir + "/trace"
        self.trace_option_dir = self.tracing_dir + "/options"
        self.trace_pid_file = self.tracing_dir + "/set_ftrace_pid"
        self.snapshot_file = self.tracing_dir + "/snapshot"

        self.required_config_options = [
            "CONFIG_FTRACE",
            "CONFIG_TRACER_SNAPSHOT"
        ]
        self.pre_flight_checks()

    def check_ftrace_options(self):
        with open("/boot/config-%s" % (release())) as f:
            config = [l.strip() for l in f.readlines()]
            for option in self.required_config_options:
                if "%s=y" % (option) not in config:
                    self.exit_with_error("Kernel not compiled with %s!" % (option))
            return False

    def exit_with_error(self, message):
        print message
        exit(1)

    def generic_disable_tracing(self):
        self.generic_filter_pid("")
        self.set_value("nop", self.current_tracer_file)

    def generic_filter_pid(self, pid):
        self.set_value(pid, self.trace_pid_file)

    def pre_flight_checks(self):
        self.check_ftrace_options()
        if not os.getuid() == 0:
            self.exit_with_error("This program needs to be executed as root")
        if not os.path.isdir(self.tracing_dir):
            self.exit_with_error(("Tracing directory %s not found. "
            "Is debugfs mounted?"
            % (self.tracing_dir)))
        self.set_value("nop", self.current_tracer_file)

    def get_setting(self, path):
        with open(path) as f:
            setting= f.readline().strip()
        return setting

    def get_trace_snapshot(self):
        self.set_value("0", self.snapshot_file)
        self.set_value("1", self.snapshot_file)
        self.set_value("", self.trace_file)
        with open(self.snapshot_file) as f:
            data = [l for l in f.readlines() if l[0] != "#"]
        return data

    def set_format_option(self, option, value):
        self.set_value(value, "%s/%s" % (self.trace_option_dir, option))

    def set_value(self, value, path):
        with open(path, "w") as f:
            f.write(value)
