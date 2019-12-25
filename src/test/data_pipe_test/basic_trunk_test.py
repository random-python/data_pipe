"""
"""

import pytest
import threading
import multiprocessing
from multiprocessing.sharedctypes import RawValue

from data_pipe.basic_trunk import *


class StatusStore(ctypes.Structure):
    "cross-process value"

    _fields_ = [
        ("value", ctypes.c_long),
    ]

    @classmethod
    def make(cls) -> ctypes.Structure:
        return RawValue(StatusStore)

    @property
    def addr(self) -> int:
        return ctypes.addressof(self)


class RPC:
    "cross-process space"

    @classmethod
    async def func_one(cls, status_addr:int, value:int) -> int:
        "cross-process function"
        status = StatusStore.from_address(status_addr)
        status.value = value
        return value * 2

    @classmethod
    async def func_two(cls, status_addr:int, value:int) -> int:
        "cross-process function"
        status = StatusStore.from_address(status_addr)
        status.value = value * 2
        return value * 3

    @classmethod
    async def func_zen(cls, value:int) -> int:
        "cross-process function"
        value = value / 0  # must fail
        return value


def verify_trunk(client_mode:TrunkMode, server_mode:TrunkMode, runner_class):

    runner_name = runner_class.__name__
    print(f"runner={runner_name} :: client={client_mode.name} server={server_mode.name}")

    counter = StatusStore.make()
    assert counter.value == 0

    status_one = StatusStore.make()
    assert status_one.value == 0

    status_two = StatusStore.make()
    assert status_two.value == 0

    def error_tracer(request, func, args, error,):
        counter.value += 1
        assert request is not None
        assert func == RPC.func_zen
        assert args == (3,)
        assert type(error) == ZeroDivisionError

    basic_trunk = BasicTrunk(error_tracer=error_tracer)

    async def server_task():
        await basic_trunk.server_main()

    async def client_task():
        assert await basic_trunk.invoke(RPC.func_one, status_one.addr, 1) == 2
        assert await basic_trunk.invoke(RPC.func_two, status_two.addr, 2) == 6
        with pytest.raises(InvocationError):
            await basic_trunk.invoke(RPC.func_zen, 3)

    def server_main():
        BasicTrunk.invoke_main(server_mode, server_task)

    def client_main():
        BasicTrunk.invoke_main(client_mode, client_task)

    server_runner = runner_class(target=server_main)
    client_runner = runner_class(target=client_main)

    server_runner.name = "server_runner"
    client_runner.name = "client_runner"

    server_runner.daemon = True
    client_runner.daemon = True

    server_runner.start()
    client_runner.start()

    client_runner.join()
    basic_trunk.terminate()
    server_runner.join()

    assert counter.value == 1
    assert status_one.value == 1
    assert status_two.value == 4


def test_trunk():
    print()
    for runner_class in [threading.Thread, multiprocessing.Process]:
        for client_mode in TrunkMode:
            for server_mode in TrunkMode:
                verify_trunk(client_mode, server_mode, runner_class)
