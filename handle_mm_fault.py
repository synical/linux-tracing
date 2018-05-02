#!/usr/bin/env python

import argparse
import re

from time import sleep

from tracing import utils
from tracing.ftrace import kprobe

"""
  x86 specific tracing of handle_mm_fault
"""

class MMFault(object):

    def __init__(self, pid_filter=False, trace_tasks=False, interval=1):
        self.interval = interval
        self.kp = kprobe.Kprobe()

        if pid_filter:
            if trace_tasks:
                pids = utils.get_tasks_for_pid(pid_filter)
            else:
                pids = [pid_filter]
            self.kp.set_event_pids(pids=pids)

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
        self.fault_pid = ""
        self.probe = "p:handle_mm_fault handle_mm_fault vm_area_struct=%di address=%si flags=%dx"
        self.split_line = []

    def disable_and_exit(self):
        self.kp.disable_tracing()
        exit(0)

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
        print "PID: %s" % (self.fault_pid)
        print "vm_area_struct: %s" % (self.vm_area_struct)
        print "Address: %s" % (self.address)
        print "Flags: %s (%s)" % (self.flags, self.parsed_fault_flags)
        print

    def trace(self):
        self.kp.set_event(self.probe)
        self.kp.enable_tracing()
        try:
            while True:
                for line in self.kp.get_trace_snapshot():
                    split_line = filter(None, line.replace(":", "").split(" "))
                    if split_line:
                        self.fault_pid = split_line[0]
                        self.parse_probe_vars(line)
                        self.parse_fault_flags()
                        self.print_fault()
                sleep(float(self.interval))
        except KeyboardInterrupt:
            self.disable_and_exit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pid", action="store", dest="pid", required=False, help="PID")
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=1, help="Collection interval")
    parser.add_argument("-t", "--tasks", action="store_true", dest="trace_tasks", default=False, help="Trace all tasks under PID")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    mm = MMFault(pid_filter=args.pid, trace_tasks=False, interval=args.interval)
    mm.trace()

if __name__ == '__main__':
    main()
