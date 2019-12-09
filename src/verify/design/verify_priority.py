"""

#1 install package
sudo pip install data_pipe

#2 use super user
sudo python

#3 run test
from data_pipe import native_module
native_module.py_set_realtime_priority()

# result
sudo python
Python 3.8.0 (default, Oct 23 2019, 18:51:26) 
[GCC 9.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from data_pipe import native_module
>>> native_module.py_set_realtime_priority()
policy ok: 99
>>> 

"""

from data_pipe.native_module import *
from data_pipe_test.verify_index import *


def verify_native_priority():
    py_set_realtime_priority()


verify_native_priority()
