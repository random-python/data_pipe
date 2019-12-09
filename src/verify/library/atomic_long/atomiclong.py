"""
https://github.com/dreid/atomiclong/blob/master/atomiclong.py
https://gcc.gnu.org/onlinedocs/gcc/_005f_005fsync-Builtins.html#g_t_005f_005fsync-Builtins
"""

from cffi import FFI

from functools import total_ordering

ffi = FFI()

ffi.cdef("""

long long_add_and_fetch(long *, long);

long long_sub_and_fetch(long *, long);

long long_bool_compare_and_swap(long *, long, long);

long long_value_compare_and_swap(long *, long, long);

void issue_barrier();

""")

lib = ffi.verify("""

long long_add_and_fetch(long *v, long l) {
    return __sync_add_and_fetch(v, l);
};

long long_sub_and_fetch(long *v, long l) {
    return __sync_sub_and_fetch(v, l);
};

long long_bool_compare_and_swap(long *v, long o, long n) {
    return __sync_bool_compare_and_swap(v, o, n);
};

long long_value_compare_and_swap(long *v, long o, long n) {
    return __sync_val_compare_and_swap(v, o, n);
};

void issue_barrier() {
    __sync_synchronize();
};

""")


@total_ordering
class AtomicLong(object):

    def __init__(self, value):
        self.store = ffi.new('long *', value)

    def __repr__(self):
        return '<{0} at 0x{1:x}: {2!r}>'.format(
            self.__class__.__name__, id(self), self.value)

    @property
    def value(self):
        return self.store[0]

    @value.setter
    def value(self, new):
        lib.long_bool_compare_and_swap(self.store, self.value, new)

    def __iadd__(self, inc):
        lib.long_add_and_fetch(self.store, inc)
        return self

    def __isub__(self, dec):
        lib.long_sub_and_fetch(self.store, dec)
        return self

    def __eq__(self, other):
        # This is needed because between `self.value` and `other.value` being
        # evaluated it's possible for the value to be changed (and since this
        # is a library predicated on threads being a thing, we have to care
        # about such rare race conditions)
        if self is other:
            return True
        elif isinstance(other, AtomicLong):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        # See __eq__ for an explanation of why this is a thing.
        if self is other:
            return False
        elif isinstance(other, AtomicLong):
            return self.value < other.value
        else:
            return self.value < other
