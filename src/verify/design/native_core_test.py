"""
"""

from hypothesis import given, example, settings
import hypothesis.strategies as st

from data_pipe.native_module import lib as LIB  # @UnresolvedImport
from data_pipe.native_module import ffi as FFI  # @UnresolvedImport

LONG_MIN = -9223372036854775808
LONG_MAX = +9223372036854775807
CONSUMER_LIMIT = LIB.consumer_limit()


def test_store_default():
    print()
    store = FFI.new('sequence_store *')
    assert store.entry_count == 0
    assert store.producer_sequence == 0
    assert store.consumer_count == 0
    assert list(store.consumer_sequence_list) == [0 for _ in range(CONSUMER_LIMIT)]


@given(
    cons_seq_list=st.lists(
        elements=st.integers(min_value=LONG_MIN, max_value=LONG_MAX),
        max_size=CONSUMER_LIMIT,
    )
)
def test_consumer_sequence_gate(cons_seq_list):
    store = FFI.new('sequence_store *')
    size = len(cons_seq_list)
    if size:
        store.consumer_count = size
        store.consumer_sequence_list = cons_seq_list
        source = LIB.consumer_sequence_gate(store)
        target = min(cons_seq_list)
        assert source == target


def test_producer_sequence_claim():
    print()
    store = FFI.new('sequence_store *')
    store.entry_count = 8
    store.producer_sequence = 0
    store.consumer_count = 1
    store.consumer_sequence_list = [0]
    for index in range(10):
        sequence = LIB.producer_sequence_claim(store)
        error_num = FFI.errno
        print(f"index={index} sequence={sequence} error_num={error_num}")
