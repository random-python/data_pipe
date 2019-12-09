"""
https://github.com/python-greenlet/greenlet/blob/master/benchmarks/invoke_chain.py
"""

#!/usr/bin/env python

"""Create a invoke_chain of coroutines and pass a value from one end to the other,
where each coroutine will increment the value before passing it along.
"""

import optparse
import time

import greenlet


def make_link(next_node):
    value = greenlet.getcurrent().parent.switch()
    next_node.switch(value + 1)


def invoke_chain(count:int):
    this_node = greenlet.getcurrent()
    for _ in range(count):
        next_node = greenlet.greenlet(make_link)
        next_node.switch(this_node)
        this_node = next_node
    return this_node.switch(0)


if __name__ == '__main__':

    count = int(1e5)

    p = optparse.OptionParser(usage='%prog [-n NUM_COROUTINES]', description=__doc__)

    p.add_option(
        '-n', type='int', dest='num_greenlets', default=count,
        help='The number of greenlets in the invoke_chain.'
    )

    options, args = p.parse_args()

    if len(args) != 0:
        p.error('unexpected arguments: %s' % ', '.join(args))

    time_start = time.time()
    green_chain = invoke_chain(options.num_greenlets)
    time_finish = time.time()
    time_diff = time_finish - time_start
    time_unit = int(1e6 * time_diff / count)
    print(f"time_unit={time_unit} micro")
