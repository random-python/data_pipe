"""
"""

import struct

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BufferPacker:
    ""

    buffer:memoryview

    # ========================================================================
    # Integer numbers
    # ========================================================================

    packer_s1 = struct.Struct('b')
    packer_s2be = struct.Struct('>h')
    packer_s4be = struct.Struct('>i')
    packer_s8be = struct.Struct('>q')
    packer_s2le = struct.Struct('<h')
    packer_s4le = struct.Struct('<i')
    packer_s8le = struct.Struct('<q')

    packer_u1 = struct.Struct('B')
    packer_u2be = struct.Struct('>H')
    packer_u4be = struct.Struct('>I')
    packer_u8be = struct.Struct('>Q')
    packer_u2le = struct.Struct('<H')
    packer_u4le = struct.Struct('<I')
    packer_u8le = struct.Struct('<Q')

    # ------------------------------------------------------------------------
    # Signed
    # ------------------------------------------------------------------------

    def read_s1(self):
        return BufferPacker.packer_s1.unpack(self.read_bytes(1))[0]

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_s2be(self):
        return BufferPacker.packer_s2be.unpack(self.read_bytes(2))[0]

    def read_s4be(self):
        return BufferPacker.packer_s4be.unpack(self.read_bytes(4))[0]

    def read_s8be(self):
        return BufferPacker.packer_s8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_s2le(self):
        return BufferPacker.packer_s2le.unpack(self.read_bytes(2))[0]

    def read_s4le(self):
        return BufferPacker.packer_s4le.unpack(self.read_bytes(4))[0]

    def read_s8le(self):
        return BufferPacker.packer_s8le.unpack(self.read_bytes(8))[0]

    # ------------------------------------------------------------------------
    # Unsigned
    # ------------------------------------------------------------------------

    def read_u1(self):
        return BufferPacker.packer_u1.unpack(self.read_bytes(1))[0]

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_u2be(self):
        return BufferPacker.packer_u2be.unpack(self.read_bytes(2))[0]

    def read_u4be(self):
        return BufferPacker.packer_u4be.unpack(self.read_bytes(4))[0]

    def read_u8be(self):
        return BufferPacker.packer_u8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_u2le(self):
        return BufferPacker.packer_u2le.unpack(self.read_bytes(2))[0]

    def read_u4le(self):
        return BufferPacker.packer_u4le.unpack(self.read_bytes(4))[0]

    def read_u8le(self):
        return BufferPacker.packer_u8le.unpack(self.read_bytes(8))[0]

    # ========================================================================
    # Floating point numbers
    # ========================================================================

    packer_f4be = struct.Struct('>f')
    packer_f8be = struct.Struct('>d')
    packer_f4le = struct.Struct('<f')
    packer_f8le = struct.Struct('<d')

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_f4be(self):
        return BufferPacker.packer_f4be.unpack(self.read_bytes(4))[0]

    def read_f8be(self):
        return BufferPacker.packer_f8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_f4le(self):
        return BufferPacker.packer_f4le.unpack(self.read_bytes(4))[0]

    def read_f8le(self):
        return BufferPacker.packer_f8le.unpack(self.read_bytes(8))[0]
