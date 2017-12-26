import os

class Ftrace(object):

    def __init__(self):
        self.tracing_path = "/sys/kernel/debug/tracing"
        self.current_tracer_path = self.tracing_path + "/current_tracer"
        self.pre_flight_checks()

    def pre_flight_checks(self):
        if not os.getuid() == 0:
            print "This program needs to be executed as root"
            exit(1)
        if not os.path.isdir(self.tracing_path):
            print """Tracing directory (%s) not found.
            Is debugfs mounted?""" % (self.tracing_path)
            exit(1)
        self.check_nop()

    def check_enabled(self):
        with open(self.tracing_path + "/tracing_on") as f:
            tracing_on = f.read(1)
            if tracing_on == 1:
                print """Tracing currently enabled.
                Please echo 0 > %s""" % (self.tracing_path+"/tracing_on")

    def check_nop(self):
        with open(self.current_tracer_path) as f:
            current_tracer = f.readline().strip()
            if current_tracer != "nop":
                print """Tracer currently set to %s.
                Please echo nop > %s before running this program""" \
                % (current_tracer, self.current_tracer_path)
                exit(1)
