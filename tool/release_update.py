#!/usr/bin/env python

"""
PyPi release rotation
"""

import os

from devrepo import base_dir
from pypirepo import perform_update

project_dir = base_dir()
project_name = 'data_pipe'

perform_update(project_dir, project_name)

# os.chdir(project_dir)
# os.system(f'rm -rf dist')
# os.system(f'python setup.py sdist --formats=zip')
