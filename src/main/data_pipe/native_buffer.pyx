# cython: language_level=3
# cython: boundscheck=False

cimport cython

cdef class NativeBuffer:
    "TODO"

    #@cython.iterable_coroutine
    async def hello_async(self):
        ""
        await self.waiter
