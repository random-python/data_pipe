"""
"""

from dataclasses import dataclass, field

from data_pipe.any_buffer import AnyBufferCore
from data_pipe.runtime_library import NativeIndex  # @UnresolvedImport


@dataclass(frozen=True)
class NativeBuffer(AnyBufferCore):
    ""

    _ring_index:NativeIndex = field(default_factory=NativeIndex, repr=False)
