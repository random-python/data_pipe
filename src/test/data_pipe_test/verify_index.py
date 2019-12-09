"""
"""


def verify_index(index_store:"AnyIndex"):
    print()

    print(f"index_store: {index_store}")

    index_store.setup(ring_size=4, wait_size=10)

    assert index_store.reader_seq == -1
    assert index_store.writer_seq == -1

    print("mask_index", hex(index_store.mask_index))
    assert index_store.mask_index == 0x3

    print("mask_limit", hex(index_store.mask_limit))
    assert index_store.mask_limit == 0x7

    # ##

    source = [(0, -1, 0), (1, -1, 1), (2, -1, 2), (3, -1, 3), (-1, -1, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_writer(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 0, 3), (1, 1, 3), (2, 2, 3), (3, 3, 3), (-1, 3, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_reader(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 3, 4), (1, 3, 5), (2, 3, 6), (3, 3, 7), (-1, 3, 7)]
    target = []

    for index in range(5):
        entry = (index_store.next_writer(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 4, 7), (1, 5, 7), (2, 6, 7), (3, 7, 7), (-1, 7, 7)]
    target = []

    for index in range(5):
        entry = (index_store.next_reader(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 7, 0), (1, 7, 1), (2, 7, 2), (3, 7, 3), (-1, 7, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_writer(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

    # ##

    source = [(0, 0, 3), (1, 1, 3), (2, 2, 3), (3, 3, 3), (-1, 3, 3)]
    target = []

    for index in range(5):
        entry = (index_store.next_reader(), index_store.reader_seq, index_store.writer_seq)
        target.append(entry)

    print(target)
    assert source == target

