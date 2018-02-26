#!/usr/bin/env python

import re

from tracing.ftrace import kprobe

"""
  x86 specific tracing of handle_mm_fault
"""

class MMFault(object):

    def __init__(self):
        self.kp = kprobe.Kprobe()
        self.fault_flags = [
            "FAULT_FLAG_WRITE",
            "FAULT_FLAG_MKWRITE",
            "FAULT_FLAG_ALLOW_RETRY",
            "FAULT_FLAG_RETRY_NOWAIT",
            "FAULT_FLAG_KILLABLE",
            "FAULT_FLAG_TRIED",
            "FAULT_FLAG_USER",
            "FAULT_FLAG_REMOTE",
            "FAULT_FLAG_INSTRUCTION",
        ]
        self.parsed_fault_flags = []
        self.pid = ""
        self.probe = "p:handle_mm_fault handle_mm_fault vm_area_struct=%di address=%si flags=%dx"
        self.split_line = []

    def parse_hex(self, hex_string):
        return bin(int(hex_string, 16))[2:].zfill(12)

    def parse_fault_flags(self):
        self.parsed_fault_flags = []
        bits = list(reversed(self.parse_hex(self.flags)))
        for x, y in enumerate(bits):
            if bits[x] == "1":
                self.parsed_fault_flags.append(self.fault_flags[x])
        self.parsed_fault_flags = "|".join(self.parsed_fault_flags)

    def parse_probe_vars(self, probe_string):
        self.flags = re.search("flags=(0x.+)", probe_string).groups()[0]
        self.vm_area_struct = re.search("vm_area_struct=([^\s]+)", probe_string).groups()[0]
        self.address = re.search("address=([^\s]+)", probe_string).groups()[0]

    def print_fault(self):
        print "PID: %s" % (self.pid)
        print "vm_area_struct: %s" % (self.vm_area_struct)
        print "Address: %s" % (self.address)
        print "Flags: %s (%s)" % (self.flags, self.parsed_fault_flags)
        print

    def trace(self):
        self.kp.set_event(self.probe)
        self.kp.enable_tracing()
        for line in self.kp.get_trace_snapshot():
            if line[0] != "#" and "handle_mm_fault" in line:
                split_line = filter(None, line.replace(":", "").split(" "))
                self.pid = split_line[0]
                self.parse_probe_vars(line)
                self.parse_fault_flags()
                self.print_fault()
        self.kp.disable_tracing()

def main():
    mm = MMFault()
    mm.trace()

if __name__ == '__main__':
    main()
