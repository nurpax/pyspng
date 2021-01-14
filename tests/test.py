
import numpy as np
import os
import io
import itertools
import pyspng as m

print ('pyspng version', m.__version__)

fname = os.path.join(os.path.dirname(__file__), 'test.png')

def synthetic_test():
    try:
        import PIL.Image
    except:
        print ('Pillow not installed.  Skipping cross comparison test.')

    alphas = [0, 64, 192, 255]
    widths = [15, 16, 32, 64]
    print ('testing', end='')
    for (w, h, a) in itertools.product(widths, widths, alphas):
        x, y, c = np.mgrid[:h, :w, :1]
        # RGB with alpha
        src_img = np.concatenate([y*3, x*3, c+a/2, c+a], axis=2).astype(np.uint8)

        #for fmt in ['L', 'LA', 'RGB', 'RGBA']:  'LA' see bug in libspng
        for fmt in ['L', 'RGB', 'RGBA']:
            if fmt == 'L':
                pil_img = PIL.Image.fromarray(src_img[:,:,0], fmt)
            elif fmt == 'LA':
                pil_img = PIL.Image.fromarray(src_img[:,:,[0,3]], fmt)
            elif fmt == 'RGB':
                pil_img = PIL.Image.fromarray(src_img[:,:,:3], fmt)
            elif fmt == 'RGBA':
                pil_img = PIL.Image.fromarray(src_img, fmt)
            stream = io.BytesIO()
            pil_img.save(stream, format='png', compress_level=0)
            bytes = stream.getvalue()

            # Load the saved PNG using pyspng by telling it what format to expect
            nparr = m.load(bytes, format=fmt)
            assert np.all(nparr == np.array(pil_img))
            # The same except let pyspng figure out the format
            # TODO
            print ('.', end='')
    print ('')

def ref_compare(fn, spngarr):
    try:
        import PIL.Image
        img = PIL.Image.open(fn).convert('RGB')
        pil_arr = np.array(img)

        # Match that loading the same image with PIL.Image produces
        # the same bits.
        assert np.all((spngarr - pil_arr) == 0)
        print ('PIL image compare ok.')
    except:
        print ('Skipping test.  PIL.Image not installed')


with open(fname, 'rb') as fin:
    sarr = m.load(fin.read(), 'RGB')
    print ('shape:', sarr.shape, 'dtype:', sarr.dtype)
    ref_compare(fname, sarr)

try:
    m.load(b'this is not a png', 'RGB')
except Exception as e:
    assert 'could not decode image size' in str(e)

synthetic_test()

print ('All tests ok.')
