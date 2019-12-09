"""
"""

import math
import random
import ctypes
import threading
import multiprocessing

from multiprocessing.sharedctypes import RawValue, RawArray

from data_pipe.runtime_library import *
from data_pipe_test.verify_index import *


def test_index():
    print()

    index_store = ruptor_store_make()  # @UndefinedVariable
    print("index_store", index_store)

    store_size = ruptor_store_size()  # @UndefinedVariable
    print("store_size", store_size)

    store_data = RawArray(ctypes.c_char, store_size)
    print("store_data", store_data)

    ruptor_index = RuptorIndex()  # @UndefinedVariable
    ruptor_index.setup(store_data)
    print("ruptor_index", ruptor_index)

    print("ruptor_index", ruptor_index.ring_size)
    print("ruptor_index", ruptor_index.wait_size)

# def test_index_store():
#     store_size = ruptor_store_size()  # @UndefinedVariable
#     store_data = RawArray(ctypes.c_char, store_size)
#     ruptor_index = RuptorIndex()  # @UndefinedVariable
#     verify_index(ruptor_index)


def test_buffer_wait_list():
    print()

    buffer = RuptorBuffer()  # @UndefinedVariable
    print("buffer", buffer)

    wait_lower = 10e-6
    wait_upper = 10e-3
    wait_size = 10
    delta = wait_lower * 1e-3

    wait_list = buffer.calc_wait_list(wait_size, wait_lower, wait_upper)
    print("wait_list", wait_list)

    assert len(wait_list) == wait_size
    assert math.fabs(wait_lower - wait_list[-1]) < delta
    assert math.fabs(wait_upper - wait_list[+0]) < delta


def test_buffer_via_thread():
    print()

    store_size = ruptor_store_size()  # @UndefinedVariable
    index_store = RawArray(ctypes.c_char, store_size)

    buffer = RuptorBuffer()  # @UndefinedVariable

    buffer.setup(index_store=index_store)

    count = buffer.index.ring_size * 1000

    source = []
    target = []

    def buffer_writer_sync():
        for _ in range(count):
            index = buffer.writer_claim_sync()
            source.append(index)
            buffer.writer_commit()

    def buffer_reader_sync():
        for _ in range(count):
            index = buffer.reader_claim_sync()
            target.append(index)
            buffer.reader_commit()

    thread_writer = threading.Thread(target=buffer_writer_sync, daemon=True)
    thread_reader = threading.Thread(target=buffer_reader_sync, daemon=True)

    thread_writer.start()
    thread_reader.start()

    thread_writer.join()
    thread_reader.join()

    assert source == target


def test_buffer_via_process():
    print()

    store_size = ruptor_store_size()  # @UndefinedVariable
    index_store = RawArray(ctypes.c_char, store_size)

    buffer = RuptorBuffer()  # @UndefinedVariable

    buffer.setup(index_store=index_store)

    ring_size = buffer.index.ring_size
    count = ring_size * 1000

    ring_data = RawArray(ctypes.c_double, ring_size)
    source = RawArray(ctypes.c_double, count)
    target = RawArray(ctypes.c_double, count)

    for index in range(count):
        source[index] = random.random()
        target[index] = -2.0

    def buffer_writer_sync(buffer, ring_data, source_data):
        for source_index in range(count):
            ring_index = buffer.writer_claim_sync()
            ring_data[ring_index] = source_data[source_index]
            buffer.writer_commit()

    def buffer_reader_sync(buffer, ring_data, target_data):
        for target_index in range(count):
            ring_index = buffer.reader_claim_sync()
            target_data[target_index] = ring_data[ring_index]
            buffer.reader_commit()

    thread_writer = multiprocessing.Process(target=buffer_writer_sync, args=(buffer, ring_data, source), daemon=True)
    thread_reader = multiprocessing.Process(target=buffer_reader_sync, args=(buffer, ring_data, target), daemon=True)

    thread_writer.start()
    thread_reader.start()

    thread_writer.join()
    thread_reader.join()

    for index in range(count):
        assert source[index] == target[index], f"index={index}"
