"""
https://stackoverflow.com/questions/45060016/why-are-large-numpy-arrays-64-byte-aligned-but-not-smaller-ones
"""

import numpy as np

print(f"start")

data_size = 1024

data_list = []
addr_list = []

for index in range(1000):

    data = np.ones(data_size).astype(np.int64)
    data_list.append(data)

    addr = data.__array_interface__['data'][0]

    assert addr % 64 == 0 , f"addr={addr} index={index}"

    assert addr not in addr_list, f"duplicate index={index}"

    addr_list.append(addr)

print(f"finish")
