"""
"""

from data_pipe.any_buffer import *


def test_any_buffer():
    print()
    source = [0.16384, 0.08192, 0.04096, 0.02048, 0.01024, 0.00512, 0.00256, 0.00128, 0.00064, 0.00032, 0.00016, 8e-05, 4e-05, 2e-05, 1e-05]
    target = AnyBufferBase.default_wait_list
    print(target)
    assert source == target
