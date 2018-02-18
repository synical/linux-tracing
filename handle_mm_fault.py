#!/usr/bin/env python

import re

from tracing.ftrace import kprobe

"""
  x86 specific tracing of handle_mm_fault
"""

class MMFault(object):

    def __init__(self):
        self.kp = kprobe.Kprobe()
        self.probe = "p:handle_mm_fault handle_mm_fault vm_area_struct=%di address=%si flags=%dx"
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

    def get_probe_vars(self, probe_string):
        flags = re.search("flags=(0x.+)", probe_string).groups()[0]
        vm_area_struct = re.search("vm_area_struct=([^\s]+)", probe_string).groups()[0]
        address = re.search("address=([^\s]+)", probe_string).groups()[0]
        return vm_area_struct, address, flags

    def parse_hex(self, hex_string):
        return bin(int(hex_string, 16))[2:].zfill(12)

    def parse_fault_flags(self, flags):
        print flags,
        bits = list(reversed(self.parse_hex(flags)))
        for x, y in enumerate(bits):
            if bits[x] == "1":
                print self.fault_flags[x],
        print

    def trace(self):
        self.kp.set_event(self.probe)
        self.kp.enable_tracing()
        for line in self.kp.get_trace_snapshot():
            if line[0] != "#" and "handle_mm_fault" in line:
                vm_area_struct, address, flags = self.get_probe_vars(line)
                print line
                self.parse_fault_flags(flags)
        self.kp.disable_tracing()

def main():
    mm = MMFault()
    mm.trace()

if __name__ == '__main__':
    main()
