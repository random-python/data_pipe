#!/usr/bin/env python

"""
Use local install for manual testing
"""

from __future__ import annotations

from devrepo import base_dir, shell

project_dir = base_dir()

shell("sudo rm -rf build")
shell("sudo python setup.py install")
shell("sudo rm -rf build")
