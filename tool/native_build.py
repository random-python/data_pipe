#!/usr/bin/env python

"""
"""

from __future__ import annotations

from devrepo import base_dir, shell

project_dir = base_dir()

import os

# os.chdir(f"{project_dir}/src/main")
# os.system(f"python data_pipe/native.py")

# shell("sudo rm -rf build")
shell(f"rm -f src/main/data_pipe/*.c")
shell(f"rm -f src/main/data_pipe/*.html")
shell(f"python setup.py build_ext --inplace")
# shell(f"cython --annotate src/main/data_pipe/runtime_library.pyx")
