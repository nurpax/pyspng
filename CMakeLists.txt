# Require CMake 3.15+ (matching scikit-build-core) Use new versions of all
# policies up to CMake 3.27
cmake_minimum_required(VERSION 3.15...3.27)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX C)

# Find the module development requirements (requires FindPython from 3.17 or
# scikit-build-core's built-in backport)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 3.0 CONFIG REQUIRED)

set(ZLIB_BUILD_TESTING OFF)
set(ZLIB_BUILD_SHARED OFF)
set(ZLIB_BUILD_STATIC ON)
set(ZLIB_INSTALL OFF)
add_subdirectory(vendor/zlib-1.4)
# The static library is linked into a shared Python extension.
set_target_properties(zlibstatic PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Add a library using FindPython's tooling (pybind11 also provides a helper like
# this)
pybind11_add_module(_pyspng_c MODULE pyspng/main.cpp)
target_include_directories(_pyspng_c PRIVATE ${CMAKE_SOURCE_DIR}/vendor/libspng-0.7.4/spng)
target_compile_definitions(_pyspng_c PRIVATE SPNG_STATIC=1 VERSION_INFO=${PROJECT_VERSION})
target_link_libraries(_pyspng_c PRIVATE ZLIB::ZLIBSTATIC)

target_sources(_pyspng_c PRIVATE vendor/libspng-0.7.4/spng/spng.c)

# The install directory is the output (wheel) directory
install(TARGETS _pyspng_c DESTINATION pyspng)
