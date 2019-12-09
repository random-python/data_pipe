"""
https://github.com/dreid/atomiclong/blob/master/test_atomiclong.py
"""

from atomiclong import AtomicLong, ffi, lib

MIN = -9223372036854775808
MAX = +9223372036854775807


def test_barier():
    lib.issue_barrier()


def test_long_value():
    value_min = ffi.new('long *', MIN)
    value_max = ffi.new('long *', MAX)
    print(f"value_min={value_min} value_max={value_max}")
    print(f"value_min={value_min[0]} value_max={value_max[0]}")
    assert value_min[0] == MIN
    assert value_max[0] == MAX


def test_long_add_and_fetch():
    l = ffi.new('long *', 0)
    assert lib.long_add_and_fetch(l, 1) == 1
    assert lib.long_add_and_fetch(l, 10) == 11


def test_long_sub_and_fetch():
    l = ffi.new('long *', 0)
    assert lib.long_sub_and_fetch(l, 1) == -1
    assert lib.long_sub_and_fetch(l, 10) == -11


def test_long_bool_compare_and_swap():
    l = ffi.new('long *', 0)
    assert lib.long_bool_compare_and_swap(l, 0, 10) == True
    assert lib.long_bool_compare_and_swap(l, 1, 20) == False


def test_long_value_compare_and_swap():
    l = ffi.new('long *', 0)
    assert lib.long_value_compare_and_swap(l, 0, 10) == 0
    assert lib.long_value_compare_and_swap(l, 10, 20) == 10


def test_atomiclong_repr():
    l = AtomicLong(123456789)
    assert '<AtomicLong at ' in repr(l)
    assert '123456789>' in repr(l)


def test_atomiclong_value():
    l = AtomicLong(0)
    assert l.value == 0
    l.value = 10
    assert l.value == 10


def test_atomiclong_iadd():
    l = AtomicLong(0)
    l += 10
    assert l.value == 10


def test_atomiclong_isub():
    l = AtomicLong(0)
    l -= 10
    assert l.value == -10


def test_atomiclong_eq():
    l1 = AtomicLong(0)
    l2 = AtomicLong(1)
    l3 = AtomicLong(0)
    assert l1 == 0
    assert l1 != 1
    assert not (l2 == 0)
    assert not (l2 != 1)
    assert l1 == l3
    assert not (l1 != l3)
    assert l1 != l2
    assert not (l1 == l2)
    assert l1 == l1


def test_atomiclong_ordering():
    l1 = AtomicLong(0)
    l2 = AtomicLong(1)
    l3 = AtomicLong(0)

    assert l1 < l2
    assert l1 <= l2
    assert l1 <= l3
    assert l2 > l1
    assert l2 >= l3
    assert l2 >= l2

    assert l1 < 1
    assert l1 <= 0
    assert l1 <= 1
    assert l1 > -1
    assert l1 >= -1
    assert l1 >= 0


def test_atomiclong_self_comparison_race():
    """
    When comparing an AtomicLong to itself, it is possible that
    self.value and other.value will not be equal because the underlying
    long may have been incremented by another thread during the comparison.

    Here we simulate this situation by ensuring that AtomicLong.value returns
    two different numbers during the comparisons, by swapping out the
    underlying storage for an object that pops items off a list.
    """

    class StubStorage(object):

        def __init__(self, values):
            self._values = values

        def __getitem__(self, _idx):
            return self._values.pop()

    l1 = AtomicLong(0)

    l1.store = StubStorage([0, 1])
    assert l1 == l1

    l1.store = StubStorage([0, 1])
    assert not (l1 < l1)
