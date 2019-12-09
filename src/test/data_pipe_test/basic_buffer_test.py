"""
"""

from data_pipe.basic_buffer import *
from data_pipe_test.verify_buffer import *


def test_buffer():
    print()
    buffer = BasicBuffer()
    verify_buffer_sync(buffer)
