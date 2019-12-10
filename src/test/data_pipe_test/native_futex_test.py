"""
"""

import os
import platform
import math
import time
import pytest
import random
import ctypes
import threading
import multiprocessing

from multiprocessing.sharedctypes import RawValue, RawArray

from data_pipe.runtime_library import *


@pytest.mark.skip("TODO threading deadlock")
@pytest.mark.skipif(platform.system() != "Linux", reason="non-linux")
def test_futex_handshake():
    print()

    print(os.uname().sysname)

    runner_class = threading.Thread
#     runner_class = multiprocessing.Process

    resource = RawValue(ctypes.c_int)
    assert resource.value == 0

    trace_list = RawArray(ctypes.c_float, 4)
    for index in range(4):
        assert trace_list[index] == 0

    def reader_code():
        trace_list[0] = time.time()
        print("reader#1")
        invoke_futex_wait(resource)  # @UndefinedVariable
        print("reader#2")
        time.sleep(0.1)
        print("reader#3")
        trace_list[1] = time.time()

    def writer_code():
        print("writer#1")
        time.sleep(0.1)
        trace_list[2] = time.time()
        print("writer#2")
        invoke_futex_wake(resource)  # @UndefinedVariable
        print("writer#3")
        trace_list[3] = time.time()

    reader_proc = runner_class(target=reader_code, daemon=True)
    writer_proc = runner_class(target=writer_code, daemon=True)

    reader_proc.start()
    writer_proc.start()

#     reader_proc.join()
#     writer_proc.join()

    for index in range(3):
        print(f"{index} trace_list={trace_list}")
        time.sleep(1)
