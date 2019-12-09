"""
"""

from data_pipe.runtime_library import *
from data_pipe_test.verify_index import *


def test_index_store():
    index_store = NativeIndex()  # @UndefinedVariable
    verify_index(index_store)
