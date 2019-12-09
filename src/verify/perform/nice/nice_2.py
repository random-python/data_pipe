#!/usr/bin/env python

import os
import time
import threading

from elevate import elevate

thread_count = 10


def nice_perf():
    ""

    count_list = [0 for _ in range(thread_count)]

    def master_proc():
        ""
        nice = os.nice(-100)
        print(f"master nice={nice}")
        while  True:
            count_list[0] += 1

    def worker_proc(index:int):
        ""
        nice = os.nice(+100)
        print(f"worker index={index} nice={nice}")
        while  True:
            count_list[index] += 1

    master_thread = threading.Thread(target=master_proc, daemon=True)
    master_thread.setName("master")
    master_thread.start()

    for index in range(1, thread_count):
        worker_thread = threading.Thread(target=worker_proc, daemon=True, args=(index,))
        worker_thread.setName("worker")
        worker_thread.start()

    while True:
        time.sleep(1)
        total = sum(count_list)
        ratio = [int(100 * entry / total) for entry in count_list]
        print(f"ratio={ratio}")


elevate()
nice_perf()
