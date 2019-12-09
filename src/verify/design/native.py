"""
"""

import os
import cffi

this_dir = os.path.abspath(os.path.dirname(__file__))


def native_source(file_name:str) -> str:
    with open(f"{this_dir}/{file_name}", "r") as native_file:
        return native_file.read()


native_build = cffi.FFI()

native_build.cdef(
    csource=native_source("native_a.h"),
)

native_build.set_source(
    module_name="data_pipe.native_module",
    source=native_source("native_code.c"),
    include_dirs=[
        this_dir,
    ],
    extra_compile_args=[
        "-std=c99",
    ],
)

if __name__ == "__main__":
    ""

    if os.path.abspath(os.curdir) == this_dir:
        os.chdir(f"{this_dir}/../.")

    native_build.compile(
        verbose=True,
    )
