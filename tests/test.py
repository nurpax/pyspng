

import numpy as np
import pyspng as m

assert m.__version__ == '0.0.1'

with open('test.png', 'rb') as fin:
    f = m.load_png(fin.read())
    print (f.shape)
    print (f)
