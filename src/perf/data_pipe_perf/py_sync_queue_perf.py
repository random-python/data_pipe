"""
"""

import queue
from data_pipe_perf.any_buffer_perf import invoke_perf

invoke_perf(buffer_maker=lambda:queue.Queue(maxsize=256))
