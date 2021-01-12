"""Python bindings for the libspng library.

.. currentmodule:: pyspng

.. autosummary::
    :toctree: _generate

    load_png
"""

import _pyspng_c as c
import numpy as np

__version__ = c.__version__

def load_png(data: bytes) -> np.ndarray:
    return c.spng_decode_image_bytes(data, c.SPNG_FMT_RGB8)
