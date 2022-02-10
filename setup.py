from setuptools import setup, find_packages, Extension

# Available at setup time due to pyproject.toml
import pybind11

import os
import sys
import subprocess

__version__ = "0.1.0"

proj_root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(proj_root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

vendor_dir = "./vendor"
spng_dir = f'{vendor_dir}/libspng-0.7.1'
miniz_dir = f'{vendor_dir}/miniz-2.2.0'

extra_compile_args = []
if sys.platform == 'win32':
  extra_compile_args += [
    '/std:c++11', '/O2'
  ]
else:
  extra_compile_args += [
    '-std=c++11', '-O3',
  ]

# MacOS doesn't like compiling C and C++ files together, so use
# make to build a staticly linked spng.a library.
if sys.platform == 'darwin':
  extra_compile_args += [ '-stdlib=libc++', '-mmacosx-version-min=10.9' ]
  subprocess.run("make", cwd=vendor_dir)
  ext_modules = [
    Extension("_pyspng_c",
        ["pyspng/main.cpp",],
        include_dirs=[ spng_dir, pybind11.get_include() ],
        extra_link_args=['-lspng',],
        library_dirs=[ vendor_dir ],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        language="c++",
        extra_compile_args=[ "-std=c++14", "-O3" ],
    ),
  ]
else:
    extra_compile_args += [ "-DMINIZ_NO_STDIO=1", "-DSPNG_USE_MINIZ=1" ]
    ext_modules = [
        Extension("_pyspng_c",
            [ "pyspng/main.cpp", f"{miniz_dir}/miniz.c", f"{spng_dir}/spng/spng.c" ],
            include_dirs=[ spng_dir, miniz_dir, pybind11.get_include() ],
            # Example: passing in the version to the compiled code
            define_macros = [('VERSION_INFO', __version__)],
            extra_compile_args=extra_compile_args,
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
    zip_safe=False,
)
