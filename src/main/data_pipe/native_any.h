//
// expose gcc compiler intrinsics
//

#define native_synchronize __sync_synchronize
#define native_bool_compare_swap_int __sync_bool_compare_and_swap
#define native_bool_compare_swap_long __sync_bool_compare_and_swap

//
// ring buffer state provider
//

typedef struct {
    volatile int _reader_seq;
    volatile int _writer_seq;
    int _reader_wait;
    int _writer_wait;
    int _ring_size;
    int _wait_size;
    int _mask_index;
    int _mask_limit;
} native_ruptor_store __attribute__ ((aligned(32)));

//
// experimental futex study
//

#if defined(__linux__)

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <sys/syscall.h>
#include <linux/futex.h>

/*
 * "Futexes Are Tricky" / Ulrich Drepper
FUTEX WAIT
This operation causes the thread to be sus-
pended in the kernel until notified. The system call
returns with the value zero in this case. Before the
thread is suspended the value of the futex variable
is checked. If it does not have the same value as
the val1 parameter the system call immediately
returns with the error EWOULDBLOCK.
In case the timeout parameter is not NULL, the
thread is suspended only for a limited time. The
struct timespec value specifies the number of
seconds the calling thread is suspended. If the time
runs out without a notification being sent, the sys-
tem call returns with the error ETIMEDOUT.
Finally the system call can return if the thread re-
ceived a signal. In this case the error is EINTR.
The addr2 parameter is not used for this opera-
tion and no specific values have to be passed to the
kernel.
 */

/*
 * "Futexes Are Tricky" / Ulrich Drepper
FUTEX WAKE
To wake up one or more threads waiting on
a futex this operation can be used. Only the addr1,
op, and val1 parameters are used. The value of the
val1 parameter is the number of threads the caller
wants to wake. The type is int, so to wake up all
waiting threads it is best to pass INT MAX.
Usually the only values which are used are 1 and
INT MAX. Everything else makes little sense given
that the list of waiters will depend on the relative
execution time each thread gets and therefore can-
not be foreseen in general. This means it cannot be
determined from user level which threads get wo-
ken. And even if it would be possible for one situ-
ation, this is an implementation detail which might
change.. Values smaller or equal to zero are in-
valid.
The kernel does not look through the list of wait-
ers to find the highest priority thread. The normal
futexes are not realtime-safe. There might be ex-
tensions in future which are, though.
Whether the woken thread gets executed right away
or the thread waking up the others continues to run
is an implementation detail and cannot be relied
on. Especially on multi-processor systems a woken
thread might return to user level before the waking
thread. This is something we will investigate later
a bit more.
The return value of the system call is the number
of threads which have been queued and have been
woken up.
*/

int native_invoke_futex(int *uaddr, int futex_op, int val1, const struct timespec *timeout, int *uaddr2, int val3) {
    return syscall(SYS_futex, uaddr, futex_op, val1, timeout, uaddr2, val3);
}

void native_invoke_futex_wait(int *futex_addr) {
    const int futex_data = 2147483647;
    *futex_addr = futex_data;
    while (1) {
        // returns 0 if the caller was woken up
        int futex_rc = native_invoke_futex(futex_addr, FUTEX_WAIT, futex_data, NULL, NULL, 0);
        if (futex_rc == 0) {
            // assume that a return value of 0 can mean a spurious wake-up
            if (*futex_addr == futex_data) {
                return; // proper wake-up
            } else {
                continue;
            }
        } else {
            perror("invoke_futex_wait: failure#1");
            exit(1);
        }
    }
}

void native_invoke_futex_wake(int *futex_addr) {
    // returns the number of waiters that were woken up
    int futex_rc = native_invoke_futex(futex_addr, FUTEX_WAKE, INT_MAX, NULL, NULL, 0);
    if (futex_rc >= 0) {
        return;
    } else {
        perror("invoke_futex_wake: failure#1");
        exit(1);
    }
}

#endif
