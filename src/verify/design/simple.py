"""
"""

import math
import trio
import asyncio
import threading

from typing import Any
from dataclasses import dataclass, field
from trio._core._run import GLOBAL_RUN_CONTEXT
from builtins import isinstance

ConditionAny = Any


@dataclass()
class IndexStore:
    ""

    INT_MIN = -2147483648
    INT_MAX = +2147483647

    reader:int = 0
    writer:int = 0
    size:int = 0
    mask_index:int = 0

    def setup(self, size:int) -> None:
        self.size = size
        self.mask_index = (1 << size) - 1

    def stored_size(self) -> int:
        return self.writer - self.reader

    def is_empty(self) -> bool:
        return self.stored_size() == 0

    def is_filled(self) -> bool:
        return self.stored_size() == self.size

    def next_reader(self) -> int:
        if self.is_empty():
            return None
        else:
            self.reader += 1
            if self.reader == self.INT_MAX:
                self.reader = self.INT_MIN
            return self.reader & self.mask_index

    def next_writer(self) -> int:
        if self.is_filled():
            return None
        else:
            self.writer += 1
            if self.writer == self.INT_MAX:
                self.writer = self.INT_MIN
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
    async def condition_await(cls, condition:"Condition"):
        ""
        async with condition:
            await condition.wait()

    @classmethod
    def condition_await_sync(cls, condition:"Condition"):
        ""
        with condition:
            condition.wait()

#     @classmethod
#     async def condition_notify(cls, condition:"Condition"):
#         ""
#         async with condition:
#             await condition.notify()

    @classmethod
    def condition_notify_sync(cls, condition:"Condition"):
        ""
        with condition:
            condition.notify()

    @classmethod
    def provision_condition(cls) -> Any:
        if cls.has_trio_loop():
            return trio.Condition()
        if cls.has_asyncio_loop():
            return asyncio.Condition()
        else:
            return threading.Condition()


@dataclass(frozen=True)
class SimpleBuffer(SimpleBase):
    ""

    entry_count:int = field(default=128)
    entry_array:list = field(default=None, repr=False)
    index_store:IndexStore = field(default_factory=IndexStore, repr=False)

    postpone_reader_condition:ConditionAny = field(default=None, repr=False)
    postpone_writer_condition:ConditionAny = field(default=None, repr=False)

    def __post_init__(self):
        """
        """
        assert math.log(self.entry_count, 2).is_integer(), f"wrong entry_count={self.entry_count}"
        entry_array = [0 for _ in range(self.entry_count)]
        object.__setattr__(self, 'entry_array', entry_array)
        self.index_store.setup(size=self.entry_count)

    async def invoke_reader(self) -> Any:
        ""
        while True:
            index = self.index_store.next_reader()
            if index is None:
                await self.postpone_reader()
            else:
                return self.invoke_reader_value(index)

    def invoke_reader_sync(self) -> Any:
        ""
        while True:
            index = self.index_store.next_reader()
            if index is None:
                self.postpone_reader_sync()
            else:
                return self.invoke_reader_value(index)

    def invoke_reader_value(self, index:int) -> Any:
        value = self.entry_array[index]
        self.activate_writer()
        return value

    async def invoke_writer(self, value:Any) -> None:
        ""
        while True:
            index = self.index_store.next_writer()
            if index is None:
                await self.postpone_writer()
            else:
                self.invoke_writer_value(index, value)
                return

    def invoke_writer_sync(self, value:Any) -> None:
        ""
        while True:
            index = self.index_store.next_writer()
            if index is None:
                self.postpone_writer_sync()
            else:
                self.invoke_writer_value(index, value)
                return

    def invoke_writer_value(self, index:int, value:Any) -> None:
        self.entry_array[index] = value
        self.activate_reader()
        return

    def activate_reader(self) -> None:
        ""
        condition = self.postpone_reader_condition
        if condition is not None and condition.locked():
            self.condition_notify(condition)

    def activate_writer(self) -> None:
        ""
        condition = self.postpone_writer_condition
        if condition is not None and condition.locked():
            self.condition_notify(condition)

    def ensure_reader_cond(self):
        ""
        condition = self.postpone_reader_condition
        if condition is None:
            condition = self.provision_condition()
            self.postpone_reader_condition = condition
        return condition

    def ensure_writer_cond(self):
        ""
        condition = self.postpone_writer_condition
        if condition is None:
            condition = self.provision_condition()
            self.postpone_writer_condition = condition
        return condition

    async def postpone_reader(self) -> None:
        ""
        condition = self.ensure_reader_cond()
        await self.condition_await(condition)

    def postpone_reader_sync(self) -> None:
        ""
        condition = self.ensure_reader_cond()
        self.condition_await_sync(condition)

    async def postpone_writer(self) -> None:
        ""
        condition = self.ensure_writer_cond()
        await self.condition_await(condition)

    def postpone_writer_sync(self) -> None:
        ""
        condition = self.ensure_writer_cond()
        self.condition_await_sync(condition)
