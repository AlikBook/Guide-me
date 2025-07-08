# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Get the directory containing this setup.py file
current_dir = os.path.dirname(os.path.abspath(__file__))

ext = Extension(
    "yen_wrapper",
    sources=[
        os.path.join(current_dir, "yen_wrapper.pyx"), 
        os.path.join(current_dir, "yen_algorithm.c")
    ],
    include_dirs=[current_dir],
)

setup(
    name="yen-wrapper",
    version="1.0.0",
    description="Fast C implementation of Yen's K-shortest paths algorithm",
    author="Your Name",
    ext_modules=cythonize([ext], compiler_directives={'language_level': 3}),
    zip_safe=False,
    python_requires='>=3.9',
)
