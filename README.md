
**Pyspng** is a small library to for efficiently loading PNG files to numpy arrays.
Pyspng does not offer any image manipulation functionality.

Pyspng was originally written to speed up loading uncompressed (PNG compression level 0),
making the PNG file format more suitable to be used in machine learning datasets.  Pyspng
uses the native [libspng](https://github.com/randy408/libspng) library for fast PNG
decoding.  Synthetic benchmarks indicate pyspng to be roughly 2-3x faster in
loading uncompressed PNGs than the Python Pillow library.

## Example

```
import numpy as np
import pyspng

with open('test.png', 'rb') as fin:
    nparr = pyspng.load(fin.read())
```

## Installation


```
pip install pyspng
```

Note: binary wheels are built for Linux and Windows.  MacOS may not work out of the box.

## Local Development

1. Clone the git repo
2. `cd pyspng && pip install .`

## License

pyspng is provided under a BSD-style license that can be found in the LICENSE
file. By using, distributing, or contributing to this project, you agree to the
terms and conditions of this license.
