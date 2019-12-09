"""
"""

import os
import gc
import enum
import time
import ctypes
import random
import trio
import curio
import asyncio
import threading
import multiprocessing
from typing import Callable
from dataclasses import dataclass

count = int(1e5)


@enum.unique
class Mode(enum.Enum):
    ""
    SYNC = enum.auto()
    ASIO = enum.auto()
    CRIO = enum.auto()
    TRIO = enum.auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class BufferResult:
    ""
    buffer_name:str
    reader_mode:Mode
    writer_mode:Mode
    measured_time:float


def buffer_perf(
        buffer_maker:Callable,
        reader_mode=Mode.SYNC,
        writer_mode=Mode.SYNC,
#         runner_class=threading.Thread,
        runner_class=multiprocessing.Process,
    ) -> BufferResult:

    gc.collect()

    buffer = buffer_maker()
    print(f"buffer: {buffer} reader_mode={reader_mode} writer_mode={writer_mode}")

    ring_data = multiprocessing.RawArray(ctypes.c_double, buffer.index.ring_size)

    source_data = multiprocessing.RawArray(ctypes.c_double, count)
    target_data = multiprocessing.RawArray(ctypes.c_double, count)

    for index in range(count):
        source_data[index] = +random.random()
        target_data[index] = -random.random()

    def buffer_reader_sync():
        for index in range(count):
            ring_index = buffer.reader_claim_sync()
            target_data[index] = ring_data[ring_index]
            buffer.reader_commit()

    def buffer_writer_sync():
        for index in range(count):
            ring_index = buffer.writer_claim_sync()
            ring_data[ring_index] = source_data[index]
            buffer.writer_commit()

    def buffer_reader_asio():

        async def buffer_reader():
            for index in range(count):
                ring_index = await buffer.reader_claim()
                target_data[index] = ring_data[ring_index]
                buffer.reader_commit()

        asyncio.run(buffer_reader())

    def buffer_writer_asio():

        async def buffer_writer():
            for index in range(count):
                ring_index = await buffer.writer_claim()
                ring_data[ring_index] = source_data[index]
                buffer.writer_commit()

        asyncio.run(buffer_writer())

    def buffer_reader_crio():

        async def buffer_reader():
            for index in range(count):
                ring_index = await buffer.reader_claim()
                target_data[index] = ring_data[ring_index]
                buffer.reader_commit()

        curio.run(buffer_reader)

    def buffer_writer_crio():

        async def buffer_writer():
            for index in range(count):
                ring_index = await buffer.writer_claim()
                ring_data[ring_index] = source_data[index]
                buffer.writer_commit()

        curio.run(buffer_writer)

    def buffer_reader_trio():

        async def buffer_reader():
            for index in range(count):
                ring_index = await buffer.reader_claim()
                target_data[index] = ring_data[ring_index]
                buffer.reader_commit()

        trio.run(buffer_reader)

    def buffer_writer_trio():

        async def buffer_writer():
            for index in range(count):
                ring_index = await buffer.writer_claim()
                ring_data[ring_index] = source_data[index]
                buffer.writer_commit()

        trio.run(buffer_writer)

    runner_reader:Any = None
    runner_writer:Any = None

    if reader_mode == Mode.SYNC:
        runner_reader = runner_class(target=buffer_reader_sync)
    elif reader_mode == Mode.ASIO:
        runner_reader = runner_class(target=buffer_reader_asio)
    elif reader_mode == Mode.CRIO:
        runner_reader = runner_class(target=buffer_reader_crio)
    elif reader_mode == Mode.TRIO:
        runner_reader = runner_class(target=buffer_reader_trio)
    else:
        assert False, f"wrong reader_mode={reader_mode}"

    if writer_mode == Mode.SYNC:
        runner_writer = runner_class(target=buffer_writer_sync)
    elif writer_mode == Mode.ASIO:
        runner_writer = runner_class(target=buffer_writer_asio)
    elif writer_mode == Mode.CRIO:
        runner_writer = runner_class(target=buffer_writer_crio)
    elif writer_mode == Mode.TRIO:
        runner_writer = runner_class(target=buffer_writer_trio)
    else:
        assert False, f"wrong writer_mode={writer_mode}"

    runner_reader.name = reader_mode.name
    runner_reader.daemon = True
    runner_writer.name = writer_mode.name
    runner_writer.daemon = True

    time_start = time.time()

    runner_reader.start()
    runner_writer.start()

    runner_reader.join()
    runner_writer.join()

    time_finish = time.time()

    for index in range(count):
        assert source_data[index] == target_data[index], f"index={index}"

    time_diff = time_finish - time_start

    return BufferResult(
        buffer_name=buffer.__class__.__name__,
        reader_mode=reader_mode,
        writer_mode=writer_mode,
        measured_time=1e6 * time_diff / count,
    )


def invoke_perf(buffer_maker:Callable, session_size:int=1):
    for session in range(session_size):
        print(f"------ session={session} ------")
        for reader_mode in Mode:
            for writer_mode in Mode:
                result = buffer_perf(buffer_maker, reader_mode, writer_mode)
                print(f"result={result}")

#
#
#


from data_pipe.runtime_library import RuptorBuffer  # @UnresolvedImport
# from data_pipe.basic_ruptor import RuptorBuffer


def buffer_maker():

    store_size = RuptorBuffer.ruptor_store_size()
    index_store = multiprocessing.RawArray(ctypes.c_char, store_size)

    buffer = RuptorBuffer()  # @UndefinedVariable
    buffer.setup(index_store=index_store)

    return buffer


if __name__ == '__main__':
    invoke_perf(buffer_maker)
