"""
"""

import gc
import enum
import time
import trio
import curio
import asyncio
import threading
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
    ) -> BufferResult:

    gc.collect()

    buffer = buffer_maker()
    print(f"buffer: {buffer} reader_mode={reader_mode} writer_mode={writer_mode}")

    source = [index for index in range(count)]
    target = [None for index in range(count)]

    def buffer_reader_sync():
        for index in range(count):
            value = buffer.get()
            target[index] = value

    def buffer_writer_sync():
        for value in source:
            buffer.put(value)

    def buffer_reader_asio():

        async def buffer_reader():
            for index in range(count):
                value = await buffer.invoke_reader()
                target[index] = value

        asyncio.run(buffer_reader())

    def buffer_writer_asio():

        async def buffer_writer():
            for value in source:
                await buffer.invoke_writer(value)

        asyncio.run(buffer_writer())

    def buffer_reader_crio():

        async def buffer_reader():
            for index in range(count):
                value = await buffer.invoke_reader()
                target[index] = value

        curio.run(buffer_reader)

    def buffer_writer_crio():

        async def buffer_writer():
            for value in source:
                await buffer.invoke_writer(value)

        curio.run(buffer_writer)

    def buffer_reader_trio():

        async def buffer_reader():
            for index in range(count):
                value = await buffer.invoke_reader()
                target[index] = value

        trio.run(buffer_reader)

    def buffer_writer_trio():

        async def buffer_writer():
            for value in source:
                await buffer.invoke_writer(value)

        trio.run(buffer_writer)

    thread_reader:threading.Thread = None
    thread_writer:threading.Thread = None

    if reader_mode == Mode.SYNC:
        thread_reader = threading.Thread(target=buffer_reader_sync)
    elif reader_mode == Mode.ASIO:
        thread_reader = threading.Thread(target=buffer_reader_asio)
    elif reader_mode == Mode.CRIO:
        thread_reader = threading.Thread(target=buffer_reader_crio)
    elif reader_mode == Mode.TRIO:
        thread_reader = threading.Thread(target=buffer_reader_trio)
    else:
        assert False, f"wrong reader_mode={reader_mode}"

    if writer_mode == Mode.SYNC:
        thread_writer = threading.Thread(target=buffer_writer_sync)
    elif writer_mode == Mode.ASIO:
        thread_writer = threading.Thread(target=buffer_writer_asio)
    elif writer_mode == Mode.CRIO:
        thread_writer = threading.Thread(target=buffer_writer_crio)
    elif writer_mode == Mode.TRIO:
        thread_writer = threading.Thread(target=buffer_writer_trio)
    else:
        assert False, f"wrong writer_mode={writer_mode}"

    thread_reader.name = reader_mode.name
    thread_reader.daemon = True
    thread_writer.name = writer_mode.name
    thread_writer.daemon = True

    time_start = time.time()

    thread_reader.start()
    thread_writer.start()

    thread_reader.join()
    thread_writer.join()

    time_finish = time.time()

    assert source == target

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

