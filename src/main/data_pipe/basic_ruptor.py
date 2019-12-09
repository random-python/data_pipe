"""
"""

import math
import time
import trio
import curio
import asyncio
import ctypes
from trio._core._run import GLOBAL_RUN_CONTEXT
from data_pipe.runtime_library import RuptorIndex  # @UnresolvedImport


class RuptorBuffer:
    ""

    ruptor_index:RuptorIndex
    wait_list:list

    @classmethod
    def calc_wait_list(cls, wait_size:int, lower:float, upper:float) -> list:
        ""
        limit = wait_size - 1
        log_base = math.log(upper / lower) / limit
        return [lower * math.exp(index * log_base) for index in range(limit, -1, -1)]

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

    def setup(self,
            index_store:ctypes.Array,
            ring_size:int=256,
            wait_size:int=10,
            wait_lower:float=10e-6,
            wait_upper:float=10e-3,
        ):
        self.ruptor_index = RuptorIndex()
        self.ruptor_index.setup(index_store, ring_size, wait_size)
        self.wait_list = self.calc_wait_list(wait_size, wait_lower, wait_upper)

    @property
    def index(self) -> RuptorIndex:
        return self.ruptor_index

    async def reader_claim(self) -> int:
        while True:
            index = self.ruptor_index.reader_claim()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                return index

    def reader_claim_sync(self) -> int:
        while True:
            index = self.ruptor_index.reader_claim()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                return index

    def reader_commit(self) -> None:
        self.ruptor_index.reader_commit()

    async def writer_claim(self) -> int:
        while True:
            index = self.ruptor_index.writer_claim()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                return index

    def writer_claim_sync(self) -> int:
        while True:
            index = self.ruptor_index.writer_claim()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                return index

    def writer_commit(self) -> None:
        self.ruptor_index.writer_commit()
