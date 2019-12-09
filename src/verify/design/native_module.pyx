# cython: language_level=3
# cython: boundscheck=False

include "native_any.pxd"
include "native_index.pyx"
include "native_buffer.pyx"
include "native_ruptor.pyx"

"""
http://www.yonch.com/tech/82-linux-thread-priority
"""

include "native_system.pxd"

cdef void set_realtime_priority():

    # shared return value
    cdef int ret

    # operate on the current thread
    cdef pthread_t this_thread = pthread_self()

    # struct sched_param is used to store the scheduling priority
    cdef sched_param param

    # set the priority to the maximum.
    param.sched_priority = sched_get_priority_max(SCHED_FIFO);

    # attempt to set thread real-time priority
    ret = pthread_setschedparam(this_thread, SCHED_FIFO, & param)
    if ret != 0:
        print("failure to set thread realtime priority:", ret)
        return

    cdef int policy = 0;

    # verify the change in thread priority
    ret = pthread_getschedparam(this_thread, & policy, & param)
    if (ret != 0):
        print("failure to get thread realtime priority:", ret)
        return

    if policy == SCHED_FIFO:
        print("policy ok:", param.sched_priority)
    else:
        print("unexpected policy")


def py_set_realtime_priority():
    set_realtime_priority()
