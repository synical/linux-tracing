import os

from platform import release

class Ftrace(object):

    def __init__(self):
        self.tracing_path = "/sys/kernel/debug/tracing"
        self.current_tracer_path = self.tracing_path + "/current_tracer"
        self.trace_path = self.tracing_path + "/trace"
        self.tracing_on_path = self.tracing_path + "/current_tracer"
        self.tracing_options_path = self.tracing_path + "/trace_options"
        self.block_events_path = self.tracing_path + "/events/block"
        self.block_trace_enable_path = self.block_events_path + "/enable"
        self.snapshot_path = self.tracing_path + "/snapshot"

        self.CONFIG_FTRACE = "CONFIG_FTRACE"
        self.CONFIG_TRACER_SNAPSHOT = "CONFIG_TRACER_SNAPSHOT"

        self.pre_flight_checks()

    def check_ftrace_option(self, option):
        with open("/boot/config-%s" % (release())) as f:
            if "%s=y" % (option) in f.read():
                return True
            self.exit_with_error("Kernel not compiled with %s!" % (option))
            return False

    def disable_block_tracing(self):
        self.set_value("0", self.block_trace_enable_path)
        self.set_value("nop", self.current_tracer_path)

    def enable_block_tracing(self, events=None):
        self.set_value("noirq-info", self.tracing_options_path)
        if events:
            for e in events:
                self.set_value("1", "%s/%s/enable" % (self.block_events_path, e))
        else:
            self.set_value("1", self.block_trace_enable_path)
        self.set_value("blk", self.current_tracer_path)

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
        self.set_value("0", self.trace_path)
        with open(self.snapshot_path) as f:
            data = f.readlines()
        return data

    def set_value(self, value, path):
        with open(path, "w") as f:
            f.write(value)
