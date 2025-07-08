# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "yen_wrapper",
    sources=["yen_wrapper.pyx", "yen_algorithm.c"],
)

setup(
    ext_modules=cythonize([ext]),
)

