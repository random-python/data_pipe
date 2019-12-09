"""
"""

import time
import math
import trio
import curio
import asyncio

from typing import Any
from dataclasses import dataclass, field
from trio._core._run import GLOBAL_RUN_CONTEXT

from data_pipe.any_index import AnyIndexBase


class AnyBufferBase:
    ""

    default_wait_size = 15
    default_wait_list = [10e-6 * (2 ** index) for index in range(default_wait_size - 1, -1, -1)]

    @classmethod
    def has_trio_loop(cls) -> bool:
        ""
        return hasattr(GLOBAL_RUN_CONTEXT, "runner")

    @classmethod
    def has_curio_loop(cls) -> bool:
        ""
        return curio.meta.curio_running()

    @classmethod
    def has_asyncio_loop(cls) -> bool:
        ""
        return asyncio._get_running_loop() is not None

    @classmethod
    async def perform_wait(cls, wait_time:float) -> None:
        ""
        if cls.has_trio_loop():
            await trio.sleep(wait_time)
        elif cls.has_curio_loop():
            await curio.sleep(wait_time)
        elif cls.has_asyncio_loop():
            await asyncio.sleep(wait_time)
        else:
            assert False, f"wrong async"

    @classmethod
    def perform_wait_sync(cls, wait_time:float) -> None:
        ""
        time.sleep(wait_time)


@dataclass(frozen=True)
class AnyBufferCore(AnyBufferBase):
    ""

    ring_size:int = field(default=128)
    wait_list:list = field(default_factory=lambda:AnyBufferBase.default_wait_list, repr=False)

    _ring_array:list = field(default=None, repr=False, init=False)
    _ring_index:AnyIndexBase = field(default_factory=AnyIndexBase, repr=False, init=False)

    def __post_init__(self):
        ""
        assert math.log(self.ring_size, 2).is_integer(), f"wrong ring_size={self.ring_size}"
        _ring_array = [ None for _ in range(self.ring_size) ]
        object.__setattr__(self, '_ring_array', _ring_array)
        self._ring_index.setup(ring_size=self.ring_size, wait_size=len(self.wait_list))

    async def invoke_reader(self) -> Any:
        ""
        while True:
            index = self._ring_index.next_reader()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                return self._ring_array[index]

    def invoke_reader_sync(self) -> Any:
        ""
        while True:
            index = self._ring_index.next_reader()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                return self._ring_array[index]

    async def invoke_writer(self, value:Any) -> None:
        ""
        while True:
            index = self._ring_index.next_writer()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                self._ring_array[index] = value
                return

    def invoke_writer_sync(self, value:Any) -> None:
        ""
        while True:
            index = self._ring_index.next_writer()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                self._ring_array[index] = value
                return
    #
    #
    #

    get = invoke_reader_sync
    put = invoke_writer_sync
