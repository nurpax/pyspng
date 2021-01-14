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

def load(data: bytes, format: Optional[str]) -> np.ndarray:
    """
    Args:
        data (bytes): PNG data
        format (:obj:`str`, optional): Output channel format.  Auto-detect if None.
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
