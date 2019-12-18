
## data_pipe

[![Travis Status][travis_icon]][travis_link]
[![Package Version][pypi_icon]][pypi_link]
[![Python Versions][python_icon]][python_link]

### Features

Cross Thread Message Pipe:
* lock-free
* thread-safe
* exponential-back-off

Message Transfer End Points:
* any combination of: sync, trio, curio, asyncio

### Benchmark

Performance on local CPU:

cross-thread
```
sync -> sync     @ 1.0 micros/object
sync -> curio    @ 5.0 micros/object
sync -> asyncio  @ 6.0 micros/object
sync -> trio     @ 7.0 micros/object
```

cross-process
```
sync -> sync     @ 0.5 micros/object
sync -> curio    @ 0.7 micros/object
sync -> asyncio  @ 0.7 micros/object
sync -> trio     @ 0.7 micros/object
```

### Install

To install python package:

```
sudo pip install data_pipe
```

### Usage

cross-process, cross-framework **rpc**:
* [basic_trunk.py](https://github.com/random-python/data_pipe/blob/master/src/main/data_pipe/basic_trunk.py)
* [basic_trunk_test.py](https://github.com/random-python/data_pipe/blob/master/src/test/data_pipe_test/basic_trunk_test.py)

cross-process, cross-framework **queue**:
* [native_ruptor.pyx](https://github.com/random-python/data_pipe/blob/master/src/main/data_pipe/native_ruptor.pyx)
* [any_ruptor_perf.py](https://github.com/random-python/data_pipe/blob/master/src/perf/data_pipe_perf/any_ruptor_perf.py)




[travis_icon]: https://travis-ci.org/random-python/data_pipe.svg?branch=master
[travis_link]: https://travis-ci.org/random-python/data_pipe/builds

[pypi_icon]: https://badge.fury.io/py/data-pipe.svg
[pypi_link]: https://pypi.python.org/pypi/data-pipe

[python_icon]: https://img.shields.io/pypi/pyversions/data_pipe.svg
[python_link]: https://pypi.python.org/pypi/data-pipe

[tokei_icon]: https://tokei.rs/b1/github/random-python/data_pipe
[tokei_link]: https://github.com/random-python/data_pipe/tree/master/src
