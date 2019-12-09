
from data_pipe.simple2 import *

import threading


def test_index_store():
    print()

    index_store = IndexStore()
    index_store.setup(size=4, scale=1)

    assert index_store.reader == -1
    assert index_store.writer == -1

    print(hex(index_store.mask_index))
    assert index_store.mask_index == 0x3

    # ##

    source = [(0, -1, 0), (1, -1, 1), (2, -1, 2), (3, -1, 3), (None, -1, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_writer(), index_store.reader, index_store.writer)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 0, 3), (1, 1, 3), (2, 2, 3), (3, 3, 3), (None, 3, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_reader(), index_store.reader, index_store.writer)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 3, 4), (1, 3, 5), (2, 3, 6), (3, 3, 7), (None, 3, 7)]
    target = []

    for index in range(5):
        entry = (index_store.next_writer(), index_store.reader, index_store.writer)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 4, 7), (1, 5, 7), (2, 6, 7), (3, 7, 7), (None, 7, 7)]
    target = []

    for index in range(5):
        entry = (index_store.next_reader(), index_store.reader, index_store.writer)
        target.append(entry)

    print(target)
    assert source == target

    # ##


def test_simple_buffer():
    print()

    buffer = SimpleBuffer()
    print(f"buffer: {buffer}")

    count = 500

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
