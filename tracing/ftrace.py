import os

from platform import release

class Ftrace(object):

    def __init__(self):
        self.tracing_path = "/sys/kernel/debug/tracing"
        self.current_tracer_path = self.tracing_path + "/current_tracer"
        self.trace_pipe_path = self.tracing_path + "/trace_pipe"
        self.tracing_on_path = self.tracing_path + "/current_tracer"
        self.tracing_options_path = self.tracing_path + "/trace_options"
        self.block_trace_enable_path = self.tracing_path + "/events/block/enable"
        self.pre_flight_checks()

    def check_ftrace_configured(self):
        with open("/boot/config-%s" % (release())) as f:
            if "CONFIG_FTRACE=y" in f.read():
                return True
            return False

    def disable_block_tracing(self):
        self.set_value("0", self.block_trace_enable_path)
        self.set_value("nop", self.current_tracer_path)

    def enable_block_tracing(self):
        self.set_value("noirq-info", self.tracing_options_path)
        self.set_value("1", self.block_trace_enable_path)
        self.set_value("blk", self.current_tracer_path)

    def exit_with_error(self, message):
        print message
        exit(1)

    def pre_flight_checks(self):
        if not self.check_ftrace_configured():
            self.exit_with_error("Kernel not compiled with CONFIG_FTRACE!")
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

    def get_trace_data(self):
        with open(self.trace_pipe_path) as f:
            try:
                print "Collecting trace data. Ctrl-C to stop."
                while True:
                    yield f.readline()
            except KeyboardInterrupt:
                f.close()

    def set_value(self, value, path):
        with open(path, "w") as f:
            f.write(value)
