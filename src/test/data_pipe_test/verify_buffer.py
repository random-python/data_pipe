"""
"""

import threading

from data_pipe.any_buffer import AnyBufferCore


def verify_buffer_sync(buffer:AnyBufferCore):
    print()

    print(f"buffer: {buffer}")

    count = buffer.ring_size * 10

    source = []
    target = []

    def buffer_writer_sync():
        for index in range(count):
            source.append(index)
            buffer.invoke_writer_sync(index)

    def buffer_reader_sync():
        for index in range(count):
            index = buffer.invoke_reader_sync()
            target.append(index)

    thread_writer = threading.Thread(target=buffer_writer_sync, daemon=True)
    thread_reader = threading.Thread(target=buffer_reader_sync, daemon=True)

    thread_writer.start()
    thread_reader.start()

    thread_writer.join()
    thread_reader.join()

    assert source == target
