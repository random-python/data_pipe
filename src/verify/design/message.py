"""
"""

import struct

from dataclasses import dataclass, field
from data_pipe.packer import BufferPacker


@dataclass(frozen=True)
class MessageBuffer(BufferPacker):
    ""

    buffer:memoryview

