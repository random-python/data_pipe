"""
"""

from data_pipe.basic_index import *
from data_pipe_test.verify_index import *


def test_log2():
    print()
    assert integer_log2(1) == 0
    assert integer_log2(2) == 1
    assert integer_log2(4) == 2
    assert integer_log2(8) == 3


def test_index_store():
    index_store = BasicIndex()
    verify_index(index_store)
