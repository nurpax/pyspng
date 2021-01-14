"""Python bindings for the libspng library.

.. currentmodule:: pyspng

.. autosummary::
    :toctree: _generate

    load
"""

import _pyspng_c as c
import numpy as np

from typing import Optional

__version__ = c.__version__

def load(data: bytes, format: Optional[str] = None) -> np.ndarray:
    """
    Load a PNG from a bytes object and return the image data as
    a np.ndarray.

    The output `format`, if specified, can be one of "L", "LA", "RGB", "RGBA".
    If left unspecified, automatically determine it by looking at the PNG ihdr
    block.

    Args:
        data (bytes): PNG data
        format (str, optional): Output pixel format.  Auto-detect if None.

    Returns:
        numpy.ndarray: Image data as a numpy array.

        The resulting array will have shape `[height,width,channels]` if channels > 1,
        or `[height,width]` for grayscale images.

        The array dtype is either :obj:`np.uint8` or :obj:`np.uint16`, depending the desired
        output `format`, or if unspecified, depending on PNG contents.
    """
    # TODO 16 bit variants?
    cfmts = {
        'L': c.SPNG_FMT_G8,
        'LA': c.SPNG_FMT_GA8,
        'RGB': c.SPNG_FMT_RGB8,
        'RGBA': c.SPNG_FMT_RGBA8,
    }
    cfmt = cfmts[format] if format is not None else c.SPNG_FMT_AUTO
    arr = c.spng_decode_image_bytes(data, cfmt)
    if arr.shape[2] == 1:  # HWC => HW
        return arr[:,:,0]
    return arr
