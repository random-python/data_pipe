"""
"""


def integer_log2(value:int) -> int:
    result = 0
    while True:
        value >>= 1
        if value > 0:
            result += 1
        else:
            break
    return result


class BasicIndex:
    "implement ring buffer math in PY"

    __slots__ = (
        '_reader_seq',
        '_writer_seq',
        '_reader_wait',
        '_writer_wait',
        '_ring_size',
        '_wait_size',
        '_mask_index',
        '_mask_limit',
    )

    def setup(self, *, ring_size:int, wait_size:int) -> None:
        power = integer_log2(ring_size)
        scale = power + 1
        self._reader_seq = -1
        self._writer_seq = -1
        self._reader_wait = 0
        self._writer_wait = 0
        self._ring_size = ring_size
        self._wait_size = wait_size
        self._mask_index = (1 << power) - 1
        self._mask_limit = (1 << scale) - 1

    def stored_size(self) -> int:
        return (self._writer_seq - self._reader_seq) & self._mask_limit

    def is_empty(self) -> bool:
        return self.stored_size() == 0

    def is_filled(self) -> bool:
        return self.stored_size() == self._ring_size

    #
    # queue interface
    #

    def empty(self) -> bool:
        return self.is_empty()

    def full(self) -> bool:
        return self.is_filled()

    def qsize(self) -> int:
        return self.stored_size()

    @property
    def maxsize(self) -> int:
        return self._ring_size

    #
    # buffer interface
    #

    @property
    def reader_seq(self) -> int:
        return self._reader_seq

    @property
    def writer_seq(self) -> int:
        return self._writer_seq

    @property
    def reader_wait(self) -> int:
        return self._reader_wait

    @property
    def writer_wait(self) -> int:
        return self._writer_wait

    @property
    def ring_size(self) -> int:
        return self._ring_size

    @property
    def wait_size(self) -> int:
        return self._wait_size

    @property
    def mask_index(self) -> int:
        return self._mask_index

    @property
    def mask_limit(self) -> int:
        return self._mask_limit

    #
    # buffer interface
    #

    def next_reader(self) -> int:
        if self.is_empty():
            self._reader_wait += 1
            if self._reader_wait > self._wait_size:
                self._reader_wait = self._wait_size
            return -self._reader_wait
        else:
            self._reader_wait = 0
            self._reader_seq = (self._reader_seq + 1) & self._mask_limit
            return self._reader_seq & self._mask_index

    def next_writer(self) -> int:
        if self.is_filled():
            self._writer_wait += 1
            if self._writer_wait > self._wait_size:
                self._writer_wait = self._wait_size
            return -self._writer_wait
        else:
            self._writer_wait = 0
            self._writer_seq = (self._writer_seq + 1) & self._mask_limit
            return self._writer_seq & self._mask_index
