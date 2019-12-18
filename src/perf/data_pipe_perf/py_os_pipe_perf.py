"""
https://cardinalpeak.com/blog/inter-thread-communication-without-a-mutex/
"""

import gc
import os
import time
import ctypes
import threading

count = int(1e5)


def buffer_perf():
    ""

    gc.collect()

    flags = os.O_DIRECT | os.O_CLOEXEC  # packet mode, propagate exception
    reader_fd, writer_fd = os.pipe2(flags)

    source = [index for index in range(count)]
    target = [None for index in range(count)]

    def buffer_reader_sync():
        for index in range(count):
            packet = os.read(reader_fd, 8)
            addr = int.from_bytes(packet, 'little')
            value = addr  # TODO from addr
            target[index] = value

    def buffer_writer_sync():
        for value in source:
            addr = value  # TODO into addr
            packet = addr.to_bytes(8, byteorder='little')
            os.write(writer_fd, packet)

    thread_reader = threading.Thread(target=buffer_reader_sync, daemon=True)
    thread_writer = threading.Thread(target=buffer_writer_sync, daemon=True)

    time_start = time.time()

    thread_reader.start()
    thread_writer.start()

    thread_reader.join()
    thread_writer.join()

    time_finish = time.time()

#     assert source == target  # TODO

    return time_finish - time_start


def invoke_perf(session_size:int=3):
    for session in range(session_size):
        print(f"------ session={session} ------")
        time_diff = buffer_perf()
        time_unit = int(1e6 * time_diff / count)
        print(f"time_unit: {time_unit}")


invoke_perf()
