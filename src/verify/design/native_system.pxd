"""
use system calls
"""

"""
https://gitlab.com/guystreeter/python-hwloc/blob/master/linuxsched.pyx
"""

cdef extern from "<sched.h>":

#     ctypedef struct sched_param:
#         pass

    cdef struct sched_param:
        int sched_priority

    enum:
        SCHED_FIFO
        SCHED_RR
        SCHED_OTHER
        SCHED_BATCH
        SCHED_IDLE
        SCHED_DEADLINE

    int sched_get_priority_max(int policy)

    int sched_get_priority_min(int policy)

"""
https://github.com/python-llfuse/python-llfuse/blob/master/Include/pthread.pxd
"""

from posix.signal cimport sigset_t

cdef extern from "<pthread.h>":
    # POSIX says this might be a struct, but CPython (and llfuse)
    # rely on it being an integer.
    ctypedef int pthread_t

    ctypedef struct pthread_attr_t:
        pass
    ctypedef struct pthread_mutexattr_t:
        pass
    ctypedef struct pthread_mutex_t:
        pass

    enum:
        PTHREAD_CANCEL_ENABLE
        PTHREAD_CANCEL_DISABLE

    int pthread_cancel(pthread_t thread)
    int pthread_setcancelstate(int state, int * oldstate)

    pthread_t pthread_self()

    int pthread_sigmask(int how, sigset_t * set, sigset_t * oldset)
    int pthread_equal(pthread_t t1, pthread_t t2)
    int pthread_create(pthread_t * thread, pthread_attr_t * attr, void * (*start_routine) (void *), void * arg)
    int pthread_join(pthread_t thread, void ** retval)
    int pthread_kill(pthread_t thread, int sig)

    int pthread_mutex_init(pthread_mutex_t * mutex, pthread_mutexattr_t * mutexattr)
    int pthread_mutex_lock(pthread_mutex_t * mutex)
    int pthread_mutex_unlock(pthread_mutex_t * mutex)

    int pthread_setschedparam(pthread_t thread, int policy, sched_param * param)
    int pthread_getschedparam(pthread_t thread, int * policy, sched_param * param)
