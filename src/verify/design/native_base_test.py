"""
"""

import errno

import data_pipe

from data_pipe.native_module import lib as LIB  # @UnresolvedImport
from data_pipe.native_module import ffi as FFI  # @UnresolvedImport

MIN = -9223372036854775808
MAX = +9223372036854775807


def test_barier():
    LIB.issue_barrier()


def test_verify_errno():
    print()
    for index in range(3):
        result = LIB.verify_errno(index)
        error = FFI.errno
        print(f"result={result} error={error}")


def test_long_value():
    value_min = FFI.new('volatile long *', MIN)
    value_max = FFI.new('volatile long *', MAX)
#     print(f"value_min={value_min} value_max={value_max}")
#     print(f"value_min={value_min[0]} value_max={value_max[0]}")
    assert value_min[0] == MIN
    assert value_max[0] == MAX


def test_long_value_incr_and_mask():
    print()
    store = FFI.new('volatile long *', MAX - 2)
    for _ in range(8):
        point = LIB.long_value_incr_and_mask(store, 1, 0x3)
        value = hex(store[0])
        print(f"point={point} value={value}")


def long_add_and_fetch():
    store = FFI.new('volatile long *', 0)
    assert LIB.long_add_and_fetch(store, 1) == 1
    assert LIB.long_add_and_fetch(store, 10) == 11


def test_long_sub_and_fetch():
    store = FFI.new('volatile long *', 0)
    assert LIB.long_sub_and_fetch(store, 1) == -1
    assert LIB.long_sub_and_fetch(store, 10) == -11


def test_long_bool_compare_and_swap():
    store = FFI.new('volatile long *', 0)
    assert LIB.long_bool_compare_and_swap(store, 0, 10) == True
    assert LIB.long_bool_compare_and_swap(store, 1, 20) == False


def test_long_value_compare_and_swap():
    store = FFI.new('volatile long *', 0)
    assert LIB.long_value_compare_and_swap(store, 0, 10) == 0
    assert LIB.long_value_compare_and_swap(store, 10, 20) == 10
