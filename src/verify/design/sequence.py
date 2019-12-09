"""
"""

from dataclasses import dataclass

from data_pipe.native_module import lib as LIB  # @UnresolvedImport
from data_pipe.native_module import ffi as FFI  # @UnresolvedImport


@dataclass(frozen=True, init=False, repr=False)
class Sequence:

    sequence_store:bytes = None

    def __init__(self, entry_count:int=16):
        ""
        sequence_store = FFI.new('sequence_store *',
            init=dict(
                entry_count=entry_count,
            ),
        )
        object.__setattr__(self, 'sequence_store', sequence_store)

    def __repr__(self):
        name = self.__class__.__name__
        store = self.sequence_store
        return (
            f"{name}("
            f"size={store.entry_count}, "
            f"prod_seq={store.producer_sequence}, "
            f"cons_num={store.consumer_count}, "
            f"cons_seq_list={list(store.consumer_sequence_list)}, "
            f")"
        )

    def consumer_claim(self, consumer:int) -> int:
        ""

    def consumer_confirm(self, consumer:int, sequence:int) -> None:
        ""

    def consumer_pospone(self):
        ""

    def producer_claim(self) -> int:
        ""
        sequence = LIB.producer_sequence_claim(self.sequence_store)
        if FFI.errno == 0:
            return sequence
        else:
            self.producer_pospone()

    def producer_confirm(self, sequence:int) -> None:
        ""

    def producer_pospone(self):
        ""
