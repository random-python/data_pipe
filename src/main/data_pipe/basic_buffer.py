"""
"""

from dataclasses import dataclass, field

from data_pipe.any_buffer import AnyBufferCore
from data_pipe.basic_index import BasicIndex


@dataclass(frozen=True)
class BasicBuffer(AnyBufferCore):
    ""

    _ring_index:BasicIndex = field(default_factory=BasicIndex, repr=False)
