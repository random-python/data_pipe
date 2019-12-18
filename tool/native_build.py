#!/usr/bin/env python

"""
"""

from __future__ import annotations

from devrepo import base_dir, shell

project_dir = base_dir()

import os
import sys

build_entry_list = sys.argv[1:]

print(f"build_entry_list={build_entry_list}")

native_sufix_list = ('.h', '.pxd', '.pyx')


def has_native(entry_path:str):
    return entry_path.endswith(native_sufix_list)


def has_build_request(entry_list):
    for entry in entry_list:
        if has_native(entry):
            return True
    return False


def invoke_build():
    shell(f"rm -f src/main/data_pipe/*.c")
    shell(f"rm -f src/main/data_pipe/*.html")
    shell(f"python setup.py build_ext --inplace")
    # shell(f"cython --annotate src/main/data_pipe/runtime_library.pyx")


if len(build_entry_list) == 0:
    invoke_build()
elif has_build_request(build_entry_list):
    invoke_build()
