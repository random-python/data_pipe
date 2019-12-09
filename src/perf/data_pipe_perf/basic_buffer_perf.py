"""
"""

from data_pipe.basic_buffer import BasicBuffer
from data_pipe_perf.any_buffer_perf import invoke_perf

invoke_perf(buffer_maker=lambda:BasicBuffer(ring_size=256))
