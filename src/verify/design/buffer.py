"""
"""

import math
import numpy as np
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnyBuffer:
    ""

    cache_line_size = 64  # TODO use actual CPU cache line size

    entry_count:int = field(default=128)
    entry_size:int = field(default=None)

    memory_size:int = field(default=None)
    memory_array:np.array = field(default=None, repr=False)
    memory_buffer:memoryview = field(default=None, repr=False)

    def __post_init__(self):
        """
        """
        assert math.log(self.entry_count, 2).is_integer(), f"wrong entry_count={self.entry_count}"
        assert math.log(self.entry_size, 2).is_integer(), f"wrong entry_size={self.entry_size}"
        store_size = self.entry_count * self.entry_size
        self.setup_store(store_size)

    def setup_store(self, store_size:int) -> None:
        """
        ensure buffer allocation on cache line boundary
        """
        memory_array = np.zeros(store_size + self.cache_line_size)
        memory_place = memory_array .__array_interface__['data'][0]
        memory_start = memory_place % self.cache_line_size
        memory_finish = memory_start + store_size
        memory_buffer = memoryview(memory_array)[memory_start:memory_finish]
        object.__setattr__(self, 'memory_size', store_size)
        object.__setattr__(self, 'memory_array', memory_array)
        object.__setattr__(self, 'memory_buffer', memory_buffer)


@dataclass(frozen=True)
class PointerBuffer(AnyBuffer):
    "circular buffer of object pointers"

    entry_size:int = field(default=np.dtype('object').itemsize)


@dataclass(frozen=True)
class StorageBuffer(AnyBuffer):
    "circular buffer of object buffers"

    entry_size:int = field(default=128)
