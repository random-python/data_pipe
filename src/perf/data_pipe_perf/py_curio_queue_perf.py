"""
"""

import gc
import time
import curio

count = int(1e5)  # number of objects to transfer


async def buffer_perf():

    gc.collect()  # start with clean memory

    source = [index for index in range(count)]  # pre-allocate data source
    target = [None for index in range(count)]  # pre-allocate data target

    async def producer(queue):
        for value in source:
            await queue.put(value)
        await queue.put(None)

    async def consumer(queue):
        index = 0
        while True:
            value = await queue.get()
            if value is None:
                break
            target[index] = value
            index += 1

    async def transfer():
        queue = curio.Queue(maxsize=256)
        writer = await curio.spawn(producer, queue)
        reader = await curio.spawn(consumer, queue)
        await writer.join()
        await reader.join()

    time_start = time.time()
    await transfer()
    time_finish = time.time()
    time_diff = time_finish - time_start

    assert source == target  # verify data integrity

    return time_diff


def invoke_perf(session_size:int=3):
    for session in range(session_size):
        print(f"--- session={session} ---")
        time_diff = curio.run(buffer_perf)  # total test time
        time_unit = int(1e6 * time_diff / count)  # per-unit test time, microseconds
        print(f"count={count} time_diff={time_diff:.3f} time_unit={time_unit} micro")


invoke_perf()
