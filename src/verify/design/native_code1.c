//
//
//

#include <limits.h>
#include <stdbool.h>
#include "native_a.h"

//
// base
//

void issue_barrier() {
    __sync_synchronize();
}

long verify_errno(long number) {
    errno = number;
    return 0;
}

long long_add_and_fetch(long *value, long delta) {
    return __sync_add_and_fetch(value, delta);
}

long long_sub_and_fetch(long *value, long delta) {
    return __sync_sub_and_fetch(value, delta);
}

bool long_bool_compare_and_swap(long *value, long past_value, long next_value) {
    return __sync_bool_compare_and_swap(value, past_value, next_value);
}

long long_value_compare_and_swap(long *value, long past_value, long next_value) {
    return __sync_val_compare_and_swap(value, past_value, next_value);
}

void long_value_set(long *value, long number) {
    *value = number;
}

void long_value_set_barrier(long *value, long number) {
    *value = number;
    __sync_synchronize();
}

long long_value_incr_and_mask(long *value, long delta, long mask) {
    *value += delta;
    return *value & mask;
}

//
// core
//

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))

void initialize_store(sequence_store *store) {
    // TODO
}

long consumer_limit() {
    return CONSUMER_LIMIT;
}

long consumer_sequence_gate(sequence_store *store) {
    long baseline = LONG_MAX;
    const int limit = store->consumer_count;
    for (int index = 0; index < limit; index++) {
        const long sequence = store->consumer_sequence_list[index];
        baseline = MIN(baseline, sequence);
    }
    return baseline;
}

long producer_sequence_claim(sequence_store *store) {
    while (1) {

        // verify destination
        if (store->consumer_count <= 0) {
            errno = EAGAIN; // no consumers, producer must suspend
            return 0;
        }

        // extract sequence state
        const long entry_count = store->entry_count;
        const long consumer_gate = consumer_sequence_gate(store);
        const long producer_past = store->producer_sequence;
        const long producer_next = producer_past + 1;
        const long advanced_gate = consumer_gate + entry_count;
        const long retarded_next = producer_next - entry_count;

        // verify buffer space
        const bool has_space = //
                producer_next < advanced_gate || retarded_next < consumer_gate;

        if (!has_space) {
            errno = EAGAIN; // buffer full, producer must suspend
            return 0;
        }

        // attempt sequence claim
        const bool has_claim = __sync_bool_compare_and_swap( //
                &store->producer_sequence, producer_past, producer_next);

        if (has_claim) {
            errno = 0; // has sequence, producer must populate entry
            return producer_next;
        }

    }
}
