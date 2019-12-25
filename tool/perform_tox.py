#!/usr/bin/env python

"""
PyPi release testing.
"""

from devrepo import shell

shell(f"rm -rf .tox")
shell(f"tox")
