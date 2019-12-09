"""
"""

from data_pipe.native_buffer import NativeBuffer
from data_pipe_perf.any_buffer_perf import invoke_perf

invoke_perf(buffer_maker=lambda:NativeBuffer(ring_size=256))
