//
//
//

#include <limits.h>
#include <stdbool.h>
#include "native_a.h"

//
//
//

int strong_stored_size(strong_store *store) {
    return (store->writer_seq - store->reader_seq) & store->mask_stored;
}

bool strong_is_empty(strong_store *store) {
    return strong_stored_size(store) == 0;
}

bool strong_is_filled(strong_store *store) {
    return strong_stored_size(store) == store->total_size;
}

//
//
//

int integer_log2(int value) {
    int result = 0;
    while (value >>= 1) {
        result++;
    }
    return result;
}

void strong_setup(strong_store *store, int size) {
    store->reader_seq = -1;
    store->writer_seq = -1;
    store->total_size = size;
    int power = integer_log2(size);
    store->mask_index = (1 << power) - 1;
    store->mask_stored = (1 << (power + 1)) - 1;
}

int strong_reader_index(strong_store *store) {
    if (strong_is_empty(store)) {
        errno = EAGAIN;
        return 0;
    } else {
        store->reader_seq++;
        errno = 0;
        return store->reader_seq & store->mask_index;
    }
}

int strong_writer_index(strong_store *store) {
    if (strong_is_filled(store)) {
        errno = EAGAIN;
        return 0;
    } else {
        store->writer_seq++;
        errno = 0;
        return store->writer_seq & store->mask_index;
    }
}
