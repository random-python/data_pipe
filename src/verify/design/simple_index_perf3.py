
from data_pipe.simple3 import *

import time
import threading

count = 100000


def emtpy_call():
    pass


def perf_index_store():
    print()

    index_store = IndexStore()
    index_store.setup(256, int(math.log2(256)))

    for index in range(count):
#         emtpy_call()
        index_store.next_reader()
        index_store.next_writer()


def invoke_perf():
    time_start = time.time()
    perf_index_store()
    time_finish = time.time()
    time_delta = time_finish - time_start
    print(f"count={count} time_delta={time_delta}")


invoke_perf()
invoke_perf()
invoke_perf()
