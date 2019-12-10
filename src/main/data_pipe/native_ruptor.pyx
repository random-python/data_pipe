# cython: language_level=3
# cython: boundscheck=False
# cython: infer_types=False

import ctypes

from libc.stdint cimport uintptr_t


def invoke_futex_wait(resource:ctypes.c_int) -> None:
    ""
    assert isinstance(resource, ctypes.c_int), f"resource: wrong type {type(resource)}"
    cdef uintptr_t resource_addr = < uintptr_t > ctypes.addressof(resource)
    IF UNAME_SYSNAME == "Linux":
        native_invoke_futex_wait(< int * > resource_addr)
    ELSE:
        raise RuntimeError("failure: non-futex")


def invoke_futex_wake(resource:ctypes.c_int) -> None:
    ""
    assert isinstance(resource, ctypes.c_int), f"resource: wrong type {type(resource)}"
    cdef uintptr_t resource_addr = < uintptr_t > ctypes.addressof(resource)
    IF UNAME_SYSNAME == "Linux":
        native_invoke_futex_wake(< int * > resource_addr)
    ELSE:
        raise RuntimeError("failure: non-futex")


def ruptor_store_make() -> ctypes.Array:
    ""
    return ctypes.c_char * sizeof(native_ruptor_store)


def ruptor_store_size() -> int:
    ""
    return sizeof(native_ruptor_store)


cdef class RuptorIndex:
    ""

    cdef object _index_store  # reference keeper
    cdef native_ruptor_store * _store  # underlying struct
    cdef uintptr_t _store_addr
    cdef int _store_size

    cdef void _setup(self,
            native_ruptor_store * store,
            uintptr_t store_addr, int store_size,
            int ring_size, int wait_size,
        ):
        cdef int power = integer_log2(ring_size)
        cdef int scale = power + 1
        self._store = store
        store._reader_seq = 0
        store._writer_seq = 0
        store._reader_wait = 0
        store._writer_wait = 0
        store._ring_size = ring_size
        store._wait_size = wait_size
        store._mask_index = (1 << power) - 1
        store._mask_limit = (1 << scale) - 1
        self._store_addr = store_addr
        self._store_size = store_size

    cdef int _active_size(self):
        cdef native_ruptor_store * store = self._store
        return (store._writer_seq - store._reader_seq) & store._mask_limit

    cdef bint _is_empty(self):
        return self._active_size() == 0

    cdef bint _is_filled(self):
        return self._active_size() == self._store._ring_size

    cdef int _reader_claim(self):
        cdef native_ruptor_store * store = self._store
        if self._is_empty():
            store._reader_wait += 1
            if store._reader_wait > store._wait_size:
                store._reader_wait = store._wait_size
            return -store._reader_wait
        else:
            store._reader_wait = 0
            return store._reader_seq & store._mask_index

    cdef void _reader_commit(self):
        cdef native_ruptor_store * store = self._store
        store._reader_seq = (store._reader_seq + 1) & store._mask_limit

    cdef int _writer_claim(self):
        cdef native_ruptor_store * store = self._store
        if self._is_filled():
            store._writer_wait += 1
            if store._writer_wait > store._wait_size:
                store._writer_wait = store._wait_size
            return -store._writer_wait
        else:
            store._writer_wait = 0
            return store._writer_seq & store._mask_index

    cdef int _writer_commit(self):
        cdef native_ruptor_store * store = self._store
        store._writer_seq = (store._writer_seq + 1) & store._mask_limit

    @property
    def store_addr(self) -> int:
        return self._store_addr

    @property
    def store_size(self) -> int:
        return self._store_size

    @property
    def ring_size(self) -> int:
        return self._store._ring_size

    @property
    def wait_size(self) -> int:
        return self._store._wait_size

    def setup(self,
            index_store:ctypes.Array,
            ring_size:int=256,
            wait_size:int=10,
        ):
        ""
        assert isinstance(index_store, ctypes.Array), "index_store: wrong type"
        assert sizeof(native_ruptor_store) <= ctypes.sizeof(index_store), "index_store: wrong size"
        cdef uintptr_t store_addr = < uintptr_t > ctypes.addressof(index_store)
        cdef int store_size = ctypes.sizeof(index_store)
        cdef native_ruptor_store * store = < native_ruptor_store * > store_addr
        self._index_store = index_store
        self._setup(store, store_addr, store_size, ring_size, wait_size)

    def reader_claim(self) -> int:
        return self._reader_claim()

    def reader_commit(self) -> int:
        return self._reader_commit()

    def writer_claim(self) -> int:
        return self._writer_claim()

    def writer_commit(self) -> int:
        return self._writer_commit()

#
#
#

import math
import time
import trio
import curio
import asyncio
from trio._core._run import GLOBAL_RUN_CONTEXT

cdef class RuptorBuffer:
    ""

    cdef RuptorIndex ruptor_index
    cdef list wait_list

    @classmethod
    def ruptor_store_size(cls) -> int:
        ""
        return sizeof(native_ruptor_store)

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
            index = self.ruptor_index._reader_claim()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                return index

    def reader_claim_sync(self) -> int:
        while True:
            index = self.ruptor_index._reader_claim()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                return index

    def reader_commit(self) -> None:
        self.ruptor_index._reader_commit()

    async def writer_claim(self) -> int:
        while True:
            index = self.ruptor_index._writer_claim()
            if index < 0:
                await self.perform_wait(self.wait_list[index])
            else:
                return index

    def writer_claim_sync(self) -> int:
        while True:
            index = self.ruptor_index._writer_claim()
            if index < 0:
                self.perform_wait_sync(self.wait_list[index])
            else:
                return index

    def writer_commit(self) -> None:
        self.ruptor_index._writer_commit()
