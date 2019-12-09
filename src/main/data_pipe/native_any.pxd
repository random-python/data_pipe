# cython: language_level=3
# cython: boundscheck=False
# cython: infer_types=False

cdef extern from "native_any.h" :

    ctypedef struct ruptor_store:
        int _reader_seq
        int _writer_seq
        int _reader_wait
        int _writer_wait
        int _ring_size
        int _wait_size
        int _mask_index
        int _mask_limit

    void sync_synchronize()
    bint sync_bool_compare_swap_int(int * value, int value_past, int value_next)
    bint sync_bool_compare_swap_long(long * value, long value_past, long value_next)

cdef int integer_log2(int value):
    cdef int result = 0
    while True:
        value >>= 1
        if value > 0:
            result += 1
        else:
            break
    return result
