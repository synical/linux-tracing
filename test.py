from time import sleep
from tracing import ftrace

ft = ftrace.Ftrace()
ft.enable_block_tracing()
sleep(10)
print ft.get_trace_data()
ft.disable_block_tracing()
