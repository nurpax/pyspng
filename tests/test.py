

import numpy as np
import pyspng as m
import PIL.Image

assert m.__version__ == '0.0.1'

fname = 'test.png'
with open(fname, 'rb') as fin:
    sarr = m.load_png(fin.read())
    print (sarr.shape)

img = PIL.Image.open(fname).convert('RGB')
pil_arr = np.array(img)

# Match that loading the same image with PIL.Image produces
# the same bits.
assert np.all((sarr - pil_arr) == 0)

try:
    m.load_png(b'this is not a png')
except Exception as e:
    print (str(e))
