"""
"""

import time
import math
import trio
import asyncio
import numba

from typing import Any
from dataclasses import dataclass, field
from trio._core._run import GLOBAL_RUN_CONTEXT

index_spec = [
    ('reader', numba.int32),
    ('writer', numba.int32),
    ('total_size', numba.int32),
    ('mask_index', numba.int32),
    ('mask_stored', numba.int32),
]


@numba.jitclass(index_spec)
class IndexStore:
    ""

    def __init__(self):
        ""

    def setup(self, size, power) -> None:
        self.reader = -1
        self.writer = -1
        self.total_size = size
        self.mask_index = (1 << power) - 1
        self.mask_stored = (1 << (power + 1)) - 1

    def stored_size(self) -> int:
        return (self.writer - self.reader) & self.mask_stored

    def is_empty(self) -> bool:
        return self.stored_size() == 0

    def is_filled(self) -> bool:
        return self.stored_size() == self.total_size

    def next_reader(self) -> int:
        if self.is_empty():
            return None
        else:
            self.reader += 1
            return self.reader & self.mask_index

    def next_writer(self) -> int:
        if self.is_filled():
            return None
        else:
            self.writer += 1
            return self.writer & self.mask_index


class SimpleBase:
    ""

    @classmethod
    def has_trio_loop(cls) -> bool:
        ""
        return hasattr(GLOBAL_RUN_CONTEXT, "runner")

    @classmethod
    def has_asyncio_loop(cls) -> bool:
        ""
        return asyncio._get_running_loop() is not None

    @classmethod
    async def perform_spin(cls, spin_time:float) -> None:
        ""
        if cls.has_trio_loop():
            await trio.sleep(spin_time)
        else:
            await asyncio.sleep(spin_time)

    @classmethod
    def perform_spin_sync(cls, spin_time:float) -> None:
        ""
        time.sleep(spin_time)


@dataclass(frozen=True)
class SimpleBuffer(SimpleBase):
    ""

    spin_time:float = field(default=0.1)
    entry_count:int = field(default=128)
    entry_array:list = field(default=None, repr=False)
    index_store:IndexStore = field(default_factory=IndexStore, repr=False)

    def __post_init__(self):
        """
        """
        assert math.log(self.entry_count, 2).is_integer(), f"wrong entry_count={self.entry_count}"
        entry_array = [ None for _ in range(self.entry_count) ]
        object.__setattr__(self, 'entry_array', entry_array)
        self.index_store.setup(self.entry_count, int(math.log2(self.entry_count)))

    async def invoke_reader(self) -> Any:
        ""
        while True:
            index = self.index_store.next_reader()
            if index is None:
                await self.perform_spin(self.spin_time)
            else:
                return self.entry_array[index]

    def invoke_reader_sync(self) -> Any:
        ""
        while True:
            index = self.index_store.next_reader()
            if index is None:
                self.perform_spin_sync(self.spin_time)
            else:
                return self.entry_array[index]

    async def invoke_writer(self, value:Any) -> None:
        ""
        while True:
            index = self.index_store.next_writer()
            if index is None:
                await self.perform_spin(self.spin_time)
            else:
                self.entry_array[index] = value
                return

    def invoke_writer_sync(self, value:Any) -> None:
        ""
        while True:
            index = self.index_store.next_writer()
            if index is None:
                self.perform_spin_sync(self.spin_time)
            else:
                self.entry_array[index] = value
                return

