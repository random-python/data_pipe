# cython: language_level=3
# cython: boundscheck=False
# cython: infer_types=False

cdef extern from "native_any.h" :

    ctypedef struct native_ruptor_store:
        int _reader_seq
        int _writer_seq
        int _reader_wait
        int _writer_wait
        int _ring_size
        int _wait_size
        int _mask_index
        int _mask_limit

    void native_synchronize()
    bint native_bool_compare_swap_int(int * value, int value_past, int value_next)
    bint native_bool_compare_swap_long(long * value, long value_past, long value_next)

    IF UNAME_SYSNAME == "Linux":
        void native_invoke_futex_wait(int * futex_addr)
        void native_invoke_futex_wake(int * futex_addr)

cdef int integer_log2(int value):
    cdef int result = 0
    while True:
        value >>= 1
        if value > 0:
            result += 1
        else:
            break
    return result
