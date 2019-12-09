"""
"""

import math
import numpy as np
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StorageBuffer:
    ""

    entry_count:int = field()

    memory_array:np.array = field(default=None, repr=False)
    memory_buffer:memoryview = field(default=None, repr=False)

    cache_line_size = 64  # TODO use actual CPU cache line size

    def __post_init__(self):
        """
        ensure buffer allocation on cache line boundary
        """
        assert math.log(self.entry_count, 2).is_integer(), f"wrong entry_count={self.entry_count}"
        store_size = self.entry_count
        store_array = np.zeros(store_size + self.cache_line_size, dtype=object)
        store_place = store_array .__array_interface__['data'][0]
        store_start = store_place % self.cache_line_size
        store_buffer = memoryview(store_array)[store_start: store_start + store_size]
        object.__setattr__(self, 'store_array', store_array)
        object.__setattr__(self, 'store_buffer', store_buffer)
