
import time
import struct
import ctypes as ct
import multiprocessing as mp


class BaseSloted():
    ""
    __slots__ = [
        "data_long",
        "data_float",
    ]


class BaseSimple():
    ""
    data_long:int
    data_float:float


class BaseStruct(ct.Structure):
    ""
    _fields_ = [
        ('data_long', ct.c_long),
        ('data_float', ct.c_double)
    ]


class BasePacked():
    ""
    __slots__ = [
        "buffer",
    ]

    index_long = 0
    index_float = 8

    def __init__(self):
        self.buffer = bytearray(16)

    @property
    def data_long(self) -> int:
        return struct.unpack_from("q", self.buffer, self.index_long)[0]

    @data_long.setter
    def data_long(self, value:int):
        struct.pack_into("q", self.buffer, self.index_long, value)

    @property
    def data_float(self) -> int:
        return struct.unpack_from("d", self.buffer, self.index_float)[0]

    @data_float.setter
    def data_float(self, value:float):
        struct.pack_into("d", self.buffer, self.index_float, value)


count = int(1e6)


def invoke_perf(base):

    time_start = time.time()

    for index in range(count):
        base.data_long = index
        base.data_float = index

    time_finish = time.time()

    time_diff = time_finish - time_start
    time_unit = 1e6 * time_diff / count
    name = base.__class__

    print(f"{name} time_unit={time_unit}")


for trial in range(3):
    print(f"--- {trial} ---")
    invoke_perf(BaseSloted())
    invoke_perf(BaseSimple())
    invoke_perf(BaseStruct())
    invoke_perf(BasePacked())
