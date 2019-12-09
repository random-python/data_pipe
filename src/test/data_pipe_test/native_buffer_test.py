"""
"""

from data_pipe.native_buffer import *
from data_pipe_test.verify_buffer import *


def test_buffer():
    print()
    buffer = NativeBuffer()
    verify_buffer_sync(buffer)
