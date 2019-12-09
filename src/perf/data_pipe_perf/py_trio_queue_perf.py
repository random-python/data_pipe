"""
"""

import gc
import time
import trio

count = int(1e5)  # number of objects to transfer


async def buffer_perf():

    gc.collect()  # start with clean memory

    source = [index for index in range(count)]  # pre-allocate data source
    target = [None for index in range(count)]  # pre-allocate data target

    async def producer(writer):
        async with writer:
            for value in source:
                await writer.send(value)

    async def consumer(reader):
        async with reader:
            index = 0
            async for value in reader:
                target[index] = value
                index += 1

    async def transfer():
        async with trio.open_nursery() as nursery:
            writer, reader = trio.open_memory_channel(256)
            nursery.start_soon(producer, writer)
            nursery.start_soon(consumer, reader)

    time_start = time.time()
    await transfer()
    time_finish = time.time()
    time_diff = time_finish - time_start

    assert source == target  # verify data integrity

    return time_diff


def invoke_perf(session_size:int=3):
    for session in range(session_size):
        print(f"--- session={session} ---")
        time_diff = trio.run(buffer_perf)  # total test time
        time_unit = int(1e6 * time_diff / count)  # per-unit test time, microseconds
        print(f"count={count} time_diff={time_diff:.3f} time_unit={time_unit} micro")


invoke_perf()
