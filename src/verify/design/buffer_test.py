
from data_pipe.buffer import *


def test_buffer():
    print()

    ring = StorageBuffer(
        entry_count=128,
        entry_size=256,
    )

    print(ring)
    print(ring.memory_buffer)
