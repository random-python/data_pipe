
import dis

from data_pipe.sequence import *


def test_sequence():
    print()

    sequence = Sequence()
    print(f"sequence: {sequence}")

    sequence.producer_claim()
    print(f"sequence: {sequence}")

#     sequence.set(123)
#     print(f"sequence: {sequence}")
#
#     print (dis.dis(Sequence.producer_index_cas))
