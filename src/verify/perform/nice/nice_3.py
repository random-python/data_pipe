#!/usr/bin/env python

import os
import time
import ctypes

import multiprocessing as mp

process_count = 10

count_list = mp.RawArray(ctypes.c_long, process_count)
for index in range(process_count) :
    count_list[index] = 0


def master_code(count_list:mp.Array) -> None:
    ""
    nice = os.nice(+0)
    print(f"master nice={nice}")
    while  True:
        count_list[0] += 1


def worker_code(index:int, count_list:mp.Array) -> None:
    ""
    nice = os.nice(+100)
    print(f"worker index={index} nice={nice}")
    while  True:
        count_list[index] += 1


master_proc = mp.Process(target=master_code, args=(count_list,))
master_proc.name = "master"
master_proc.start()

for index in range(1, process_count):
    worker_proc = mp.Process(target=worker_code, args=(index, count_list,))
    worker_proc.name = f"worker-{index}"
    worker_proc.start()

while True:
    time.sleep(1)
    total = sum(count_list)
    ratio = [int(100 * entry / total) for entry in count_list]
    print(f"ratio={ratio}")
