# cython: language_level=3
# cython: boundscheck=False
# cython: infer_types=False

cdef class NativeIndex:
    "implement ring buffer math in C"

    cdef int _reader_seq
    cdef int _writer_seq
    cdef int _reader_wait
    cdef int _writer_wait
    cdef int _ring_size
    cdef int _wait_size
    cdef int _mask_index
    cdef int _mask_limit

    cdef int stored_size(self):
        return (self._writer_seq - self._reader_seq) & self._mask_limit

    cdef bint is_empty(self):
        return self.stored_size() == 0

    cdef bint is_filled(self):
        return self.stored_size() == self._ring_size

    cdef void make_setup(self, int ring_size, int wait_size):
        cdef int power = integer_log2(ring_size)
        cdef int scale = power + 1
        self._reader_seq = -1
        self._writer_seq = -1
        self._reader_wait = 0
        self._writer_wait = 0
        self._ring_size = ring_size
        self._wait_size = wait_size
        self._mask_index = (1 << power) - 1
        self._mask_limit = (1 << scale) - 1

    cdef int make_reader(self):
        if self.is_empty():
            self._reader_wait += 1
            if self._reader_wait > self._wait_size:
                self._reader_wait = self._wait_size
            return -self._reader_wait
        else:
            self._reader_wait = 0
            self._reader_seq = (self._reader_seq + 1) & self._mask_limit
            return self._reader_seq & self._mask_index

    cdef int make_writer(self):
        if self.is_filled():
            self._writer_wait += 1
            if self._writer_wait > self._wait_size:
                self._writer_wait = self._wait_size
            return -self._writer_wait
        else:
            self._writer_wait = 0
            self._writer_seq = (self._writer_seq + 1) & self._mask_limit
            return self._writer_seq & self._mask_index

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
    # index interface
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
    # index interface
    #

    def setup(self, *, int ring_size, int wait_size) -> None:
        self.make_setup(ring_size, wait_size)

    def next_reader(self) -> int:
        return self.make_reader()

    def next_writer(self) -> int:
        return self.make_writer()
