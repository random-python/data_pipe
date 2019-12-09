//
//
//

#define CONSUMER_LIMIT 16

typedef struct {
    long entry_count;
    volatile long producer_sequence;
    volatile long consumer_count;
    volatile long consumer_sequence_list[CONSUMER_LIMIT];
} sequence_store;

//
// base
//

void issue_barrier();
long verify_errno(long number);
long long_add_and_fetch(long *value, long delta);
long long_sub_and_fetch(long *value, long delta);
bool long_bool_compare_and_swap(long *value, long past_value, long next_value);
long long_value_compare_and_swap(long *value, long past_value, long next_value);
void long_value_set(long *value, long number);
void long_value_set_barrier(long *value, long number);
long long_value_incr_and_mask(long *value, long delta, long mask);

//
// core
//

long consumer_limit();
long consumer_sequence_gate(sequence_store *store);
long producer_sequence_claim(sequence_store *store);
