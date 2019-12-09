/*
 * Producer/Consumer thread communication without mutexes, by Ben
 * Mesander.
 *
 * For background, see the post http://cardinalpeak.com/blog?p=1696
 *
 * Copyright (c) 2013, Cardinal Peak, LLC.  http://cardinalpeak.com
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1) Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2) Redistributions in binary form must reproduce the above
 *    copyright notice, this list of conditions and the following
 *    disclaimer in the documentation and/or other materials provided
 *    with the distribution.
 *
 * 3) Neither the name of Cardinal Peak nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * CARDINAL PEAK, LLC BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

// to compile:
// g++ -Wall prodcons.cpp -lphthread -o prodcons
#include <stdlib.h>
#include <poll.h>
#include <unistd.h>
#include <stdio.h>
#include <pthread.h>

void consumer(int fd);
void* producer(void*);

// used to pass pipe to producer thread

struct threadargs {
    int fd;
};

// data to pass between threads

class foo {
public:
    int important;
};

// spin up producer thread -- initial thread of execution will be the
// consumer thread in this example.
int main(int argc, char **argv) {
    // create inter-thread communication pipe

    int pipefd[2];

    if (pipe(pipefd) != 0) {
        perror("pipe");
        exit(1);
    }

    // create the producer thread

    pthread_t producerthread;
    struct threadargs args;
    args.fd = pipefd[1]; // write end of the pipe
    pthread_create(&producerthread, NULL, &producer, (void*) &args);

    // go into consumer event loop

    consumer(pipefd[0]);

    // in the real world, we'd do pthread_join(), etc. here to clean up.

    return 0;
}

void consumer(int fd) {
    // set up file descriptors to do i/o on. In this example, just our
    // pipe from the consumer.

    struct pollfd fds[1];
    fds[0].fd = fd;
    fds[0].events = POLLIN;

    for (;;) {

        // wait for an event from one of our producer(s)

        if (poll(fds, 1, -1) != 1) {
            perror("poll");
            exit(1);
        }

        if (fds[0].revents != POLLIN) {
            fprintf(stderr, "unexpected poll revents: %hd\n", fds[0].revents);
            exit(1);
        }

        // read pointer to object from producer thread from pipe

        class foo *bar;
        if (read(fds[0].fd, &bar, sizeof(bar)) != sizeof(bar)) {
            perror("read");
            exit(1);
        }

        printf("the consumer got some important data from the producer: %d\n", bar->important);

        // the consumer owns the allocated object now, so it must delete it.

        delete bar;
    }
}

void* producer(void *p) {
    int i;
    int fd = reinterpret_cast<struct threadargs*>(p)->fd;

    for (i = 0;; i++) {

        // every second, create a new class containing important
        // data, and pass it to the consumer.

        sleep(1);
        class foo *bar = new foo();
        bar->important = i;
        int rc = write(fd, &bar, sizeof(bar));

        // lose our pointer to the new object so we can't inadvertently
        // reference it.

        bar = NULL;

        // in the real world, we'd likely make fd nonblocking so the
        // producer wouldn't lock up if the consumer died or got very
        // far behind.

        if (rc != sizeof(bar)) {
            perror("write");
            exit(1);
        }
    }
}
