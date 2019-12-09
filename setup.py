#!/usr/bin/env python

from setuptools import setup, Extension

setup(

    pbr=True,

    setup_requires=[
        "pbr",
        "cython"
    ],

    ext_modules=[
        Extension(
            name="data_pipe.runtime_library",
            sources=[
                "src/main/data_pipe/runtime_library.pyx",
            ],
        ),
    ]

)
