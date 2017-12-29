import os

class Ftrace(object):

    def __init__(self):
        self.tracing_path = "/sys/kernel/debug/tracing"
        self.current_tracer_path = self.tracing_path + "/current_tracer"
        self.trace_data_path = self.tracing_path + "/trace"
        self.tracing_on_path = self.tracing_path + "/current_tracer"
        self.block_trace_enable_path = self.tracing_path + "/events/block/enable"
        self.pre_flight_checks()

    def disable_block_tracing(self):
        self.set_value("0", self.block_trace_enable_path)
        self.set_value("nop", self.current_tracer_path)

    def enable_block_tracing(self):
        self.set_value("1", self.block_trace_enable_path)
        self.set_value("blk", self.current_tracer_path)

    def exit_with_error(self, message):
        print message
        exit(1)

    def pre_flight_checks(self):
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
        with open(self.trace_data_path) as f:
            data = f.read(4096)
        return data

    def set_value(self, value, path):
        with open(path, "w") as f:
            f.write(value)
