//
// expose gcc compiler intrinsics
//

#define sync_synchronize __sync_synchronize
#define sync_bool_compare_swap_int __sync_bool_compare_and_swap
#define sync_bool_compare_swap_long __sync_bool_compare_and_swap

//
//
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
} ruptor_store __attribute__ ((aligned(32)));

//
//
//

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdatomic.h>
#include <sys/syscall.h>
#include <linux/futex.h>

int invoke_futex(int *uaddr, int futex_op, int val, const struct timespec *timeout, int *uaddr2, int val3) {
    return syscall(SYS_futex, uaddr, futex_op, val, timeout, uaddr2, val3);
}

void invoke_futex_wait(int *futex_addr, int value) {
    while (1) {
        // returns 0 if the caller was woken up
        int futex_rc = invoke_futex(futex_addr, FUTEX_WAIT, value, NULL, NULL, 0);
        if (futex_rc == 0) {
            // assume that a return value of 0 can mean a spurious wake-up
            if (*futex_addr == value) {
                return;
            }
        } else if (futex_rc == -1) {
            if (errno == EAGAIN) {
                continue;
            }
            perror("invoke_futex_wait: failure#1");
            exit(1);
        } else {
            perror("invoke_futex_wait: failure#2");
            exit(1);
        }
    }
}

void invoke_futex_wake(int *futex_addr) {
    // returns the number of waiters that were woken up
    int futex_rc = invoke_futex(futex_addr, FUTEX_WAKE, INT_MAX, NULL, NULL, 0);
    if (futex_rc >= 0) {
        return;
    } else {
        perror("invoke_futex_wake: failure#1");
        exit(1);
    }
}
