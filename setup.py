from setuptools import setup, find_packages

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext

import os
import sys

__version__ = "0.1.0"

proj_root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(proj_root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

zlib_dir = 'vendor/zlib-1.2.11/'
zlib_sources = [zlib_dir + fn for fn in ['adler32.c', 'compress.c', 'crc32.c', 'deflate.c', 'gzclose.c', 'gzlib.c', 'gzread.c', 'gzwrite.c', 'infback.c', 'inffast.c', 'inflate.c', 'inftrees.c', 'trees.c', 'uncompr.c', 'zutil.c']]

ext_modules = [
    Pybind11Extension("_pyspng_c",
        ["pyspng/main.cpp", "vendor/libspng-0.6.1/spng/spng.c"] + zlib_sources,
        include_dirs=['vendor/libspng-0.6.1', zlib_dir],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
    ),
]

setup(
    name="pyspng",
    version=__version__,
    author="Janne Hellsten",
    author_email="jjhellst@gmail.com",
    url="https://github.com/nurpax/pyspng", # TODO
    description="Fast libspng-based PNG decoder",
    project_urls={
        'Documentation': 'https://pyspng.readthedocs.io/',
        'Tracker': 'https://github.com/nurpax/pyspng/issues',
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=ext_modules,
    packages=['pyspng'],
    extras_require={"test": "pytest"},
    install_requires=[
        'numpy',
    ],
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
