//
//
//

typedef struct {
    volatile int reader_seq;
    volatile int writer_seq;
    int total_size;
    int mask_index;
    int mask_stored;
} strong_store;

//
//
//

void strong_setup(strong_store *store, int size);
int strong_reader_index(strong_store *store);
int strong_writer_index(strong_store *store);
