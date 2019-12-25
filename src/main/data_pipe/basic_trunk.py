"""
cross-process, cross-framework rpc
"""

import os
import enum
import mmap
import inspect
import traceback
import pickle
import ctypes
import socket

import trio
import curio
import asyncio

from types import CoroutineType
from typing import Any, Tuple, Callable
from contextlib import contextmanager

from trio._core._run import current_task as trio_current_task
from trio._core._run import GLOBAL_RUN_CONTEXT as trio_global_context


@enum.unique
class TrunkMode(enum.Enum):
    "framework type"

    TRIO = enum.auto()
    CURIO = enum.auto()
    ASYNCIO = enum.auto()


@enum.unique
class ExecCode(enum.IntEnum):
    "server response status code"

    TERMINATE = enum.auto()
    TIMEOUT = enum.auto()
    FAILURE = enum.auto()
    SUCCESS = enum.auto()


class InvocationError(Exception):
    ""


class TerminationError(Exception):
    ""


class TrunkToken(ctypes.Structure):
    "client/server communication"

    _fields_ = [
        ("task_id", ctypes.c_long),
        ("exec_code", ctypes.c_int),
        ("meta_size", ctypes.c_int),
        ("data_size", ctypes.c_int),
    ]

    def __str__(self) -> str:
        return (
            f"Token("
            f"task_id={self.task_id},"
            f"exec_code={self.exec_code},"
            f"meta_size={self.meta_size},"
            f"data_size={self.data_size},"
            f")"
        )

    @classmethod
    def packet_decode(cls, buffer:bytes) -> Tuple:
        head_start = 0
        head_finish = ctypes.sizeof(TrunkToken)
        head_obj = TrunkToken.from_buffer_copy(buffer[head_start:head_finish])
        meta_start = head_finish
        meta_finish = meta_start + head_obj.meta_size
        meta_obj = pickle.loads(buffer[meta_start:meta_finish])
        data_start = meta_finish
        data_finish = data_start + head_obj.data_size
        data_obj = pickle.loads(buffer[data_start:data_finish])
        return (head_obj, meta_obj, data_obj)

    @classmethod
    def packet_encode(cls,
            task_id:int,
            exec_code:int,
            meta_obj:object,
            data_obj:object,
        ) -> bytes:
        meta_buf = pickle.dumps(meta_obj)
        data_buf = pickle.dumps(data_obj)
        head_obj = TrunkToken()
        head_obj.task_id = task_id
        head_obj.exec_code = exec_code
        head_obj.meta_size = len(meta_buf)
        head_obj.data_size = len(data_buf)
        head_buf = bytes(head_obj)
        buffer = head_buf + meta_buf + data_buf
        return buffer

    def has_success(self) -> bool:
        return self.exec_code == ExecCode.SUCCESS

    def has_failure(self) -> bool:
        return self.exec_code == ExecCode.FAILURE

    def has_timeout(self) -> bool:
        return self.exec_code == ExecCode.TIMEOUT

    def has_terminate(self) -> bool:
        return self.exec_code == ExecCode.TERMINATE


@contextmanager
def with_ignore_errors(*error_list):
    try:
        yield
    except error_list:
        pass


class AnyTrunk:
    "cross-framework operation support"

    PACKET_LIMIT = 64 * mmap.PAGESIZE

    @classmethod
    def has_trio_loop(cls) -> bool:
        return hasattr(trio_global_context, "runner")

    @classmethod
    def has_curio_loop(cls) -> bool:
        return curio.meta.curio_running()

    @classmethod
    def has_asyncio_loop(cls) -> bool:
        return asyncio._get_running_loop() is not None

    @classmethod
    async def wait_trio_readable(cls, fd:int) -> None:
        await trio.hazmat.wait_readable(fd)

    @classmethod
    async def wait_trio_writable(cls, fd:int) -> None:
        await trio.hazmat.wait_writable(fd)

    @classmethod
    async def wait_curio_readable(cls, fd:int) -> None:
        await curio.traps._read_wait(fd)

    @classmethod
    async def wait_curio_writable(cls, fd:int) -> None:
        await curio.traps._write_wait(fd)

    @classmethod
    async def wait_asyncio_readable(cls, fd:int) -> None:
        loop = asyncio.get_running_loop()
        future = asyncio.Future()
        future.add_done_callback(lambda *args : loop.remove_reader(fd))
        loop.add_reader(fd, future.set_result, None)
        await future

    @classmethod
    async def wait_asyncio_writable(cls, fd:int) -> None:
        loop = asyncio.get_running_loop()
        future = asyncio.Future()
        future.add_done_callback(lambda *args : loop.remove_writer(fd))
        loop.add_writer(fd, future.set_result, None)
        await future

    @classmethod
    async def wait_readable(cls, fd:int) -> None:
        "await file descrptor ready-for-read state"
        if cls.has_trio_loop():
            await cls.wait_trio_readable(fd)
        elif cls.has_curio_loop():
            await cls.wait_curio_readable(fd)
        elif cls.has_asyncio_loop():
            await cls.wait_asyncio_readable(fd)
        else:
            raise RuntimeError(f"no loop")

    @classmethod
    async def wait_writable(cls, fd:int) -> None:
        "await file descrptor ready-for-write state"
        if cls.has_trio_loop():
            await cls.wait_trio_writable(fd)
        elif cls.has_curio_loop():
            await cls.wait_curio_writable(fd)
        elif cls.has_asyncio_loop():
            await cls.wait_asyncio_writable(fd)
        else:
            raise RuntimeError(f"no loop")

    @classmethod
    def packet_read(cls, fd:int) -> bytes:
        "receive datagram packet"
        buffer = os.read(fd, cls.PACKET_LIMIT)
        recv_size = len(buffer)
        assert 0 < recv_size and recv_size < cls.PACKET_LIMIT
        return buffer

    @classmethod
    def packet_write(cls, fd:int, buffer:bytes) -> None:
        "transmit datagram packet"
        send_size = os.write(fd, buffer)
        assert send_size == len(buffer)

    @classmethod
    async def this_task(cls) -> int:
        "detect current framework task"
        if cls.has_trio_loop():
            return trio_current_task()
        elif cls.has_curio_loop():
            return await curio.current_task()
        elif cls.has_asyncio_loop():
            return asyncio.current_task()
        else:
            raise RuntimeError(f"no loop")

    @classmethod
    async def spawn_task(cls, func:CoroutineType, *args) -> "AnyTask":
        "create and launch new background task"
        if cls.has_trio_loop():
            return trio.hazmat.spawn_system_task(func, *args)
        elif cls.has_curio_loop():
            return await curio.spawn(func, *args)
        elif cls.has_asyncio_loop():
            return asyncio.create_task(func(*args))
        else:
            raise RuntimeError(f"no loop")

    @classmethod
    def invoke_main(cls, mode:TrunkMode, func:CoroutineType, *args, **kwargs) -> object:
        "create and launch main framework task"
        if mode == TrunkMode.TRIO:
            return trio.run(func, *args, **kwargs)
        elif mode == TrunkMode.CURIO:
            return curio.run(func, *args, **kwargs)
        elif mode == TrunkMode.ASYNCIO:
            return asyncio.run(func(*args, **kwargs))
        else:
            raise RuntimeError(f"no mode: {mode}")

    @classmethod
    def default_tracer(cls,
            token:TrunkToken,
            func:Callable,
            args:Tuple,
            error:Exception,
        ) -> None:
        "server error reporter"
        traceback.print_exc()


class BasicTrunk(AnyTrunk):
    "cross-process, cross-framework rpc"

    def __init__(self,
            buffer_size:int=1 * mmap.PAGESIZE,
            error_tracer:Callable=AnyTrunk.default_tracer,
        ) -> None:
        ""
        self.buffer_size = buffer_size
        self.error_tracer = error_tracer
        client_sock, server_sock = socket.socketpair(type=socket.SOCK_DGRAM)
        self.client_fd = self.__init_socket(client_sock)
        self.server_fd = self.__init_socket(server_sock)
        assert buffer_size <= mmap.PAGESIZE and buffer_size < self.PACKET_LIMIT, f"wrong buffer_size: {buffer_size}"

    def __init_socket(self, sock:socket) -> int:
        sock.setblocking(False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.buffer_size)
        sock_fd = sock.detach()
        return sock_fd

    async def invoke(self, func:CoroutineType, *args) -> Any:
        "invoke function in server process"

        assert inspect.iscoroutinefunction(func), f"need coro: {func}"

        task_id = id(await self.this_task())

        request_packet = TrunkToken.packet_encode(task_id, 0, func, args)
        assert len(request_packet) < self.buffer_size, f"request is too big"

        # send request
        await self.wait_writable(self.client_fd)
        self.packet_write(self.client_fd, request_packet)

        # receive response
        await self.wait_readable(self.client_fd)
        response_packet = self.packet_read(self.client_fd)

        # interpret result
        response, meta, data = TrunkToken.packet_decode(response_packet)
        if response.has_success():
            assert task_id == response.task_id, f"wrong response: {response}"
            return data
        elif response.has_failure():
            raise InvocationError(func, meta(*data))
        elif response.has_terminate():
            raise TerminationError()
        else:
            assert False, f"wrong response: {response}"

    async def server_main(self) -> None:
        "execute function requested from client process"
        while True:

            # receive request
            await self.wait_readable(self.server_fd)
            request_packet = self.packet_read(self.server_fd)
            request, func, args = TrunkToken.packet_decode(request_packet)

            if request.has_terminate():
                return

            # produce response
            try:
                task_id = request.task_id
                meta_obj = None
                data_obj = await func(*args)
                exec_code = ExecCode.SUCCESS
            except Exception as error:
                self.error_tracer(request, func, args, error,)
                meta_obj = type(error)
                data_obj = error.args
                exec_code = ExecCode.FAILURE

            response_packet = TrunkToken.packet_encode(task_id, exec_code, meta_obj, data_obj)
            assert len(response_packet) < self.buffer_size, f"response is too big"

            await self.wait_writable(self.server_fd)
            self.packet_write(self.server_fd, response_packet)

    def terminate(self):
        "release client and server"
        self.terminate_client()
        self.terminate_server()

    @with_ignore_errors(Exception)
    def terminate_client(self):
        "send termination signal to waiting client task"
        buffer = TrunkToken.packet_encode(0, ExecCode.TERMINATE, None, None)
        self.packet_write(self.server_fd, buffer)

    @with_ignore_errors(Exception)
    def terminate_server(self):
        "send termination signal to waiting server task"
        buffer = TrunkToken.packet_encode(0, ExecCode.TERMINATE, None, None)
        self.packet_write(self.client_fd, buffer)
