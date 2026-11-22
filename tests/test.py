
import numpy as np
import os
import io
import itertools
import pyspng as m
from pyspng import _pyspng_c as c
import glob
import struct
import zlib

print ('pyspng version', m.__version__)

fname = os.path.join(os.path.dirname(__file__), 'test.png')

def synthetic_test():
    try:
        import PIL.Image
    except:
        print ('Pillow not installed.  Skipping cross comparison test.')
        return

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
            nparr = m.load(bytes)
            assert np.all(nparr == np.array(pil_img))

            print ('.', end='')
    print ('')

def test_image_files():
    '''Test that pyspng.load() works the same way as PIL.Image.open().'''

    try:
        import PIL.Image
    except:
        print ('Pillow not installed.  Skipping png file cross comparison test.')
        return

    pngs = sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'img/*.png')))
    print ('testing image files', end='')
    for fname in pngs:

        # Test in RGBA
        pil_img = PIL.Image.open(fname)
        if pil_img.mode == 'P':
            pil_img = pil_img.convert('RGB')
            expected_spng_fmt = 'RGB'
        else:
            assert False, 'unimplemented'

        with open(fname, 'rb') as fp:
            png_bytes = fp.read()

        spng_arr_auto = m.load(png_bytes)
        spng_arr_expl = m.load(png_bytes, expected_spng_fmt)

        assert np.all(np.array(pil_img) == spng_arr_auto)
        assert np.all(np.array(pil_img) == spng_arr_expl)

        print ('.', end='')
    print ('')


def test_trns():
    assert isinstance(c.SPNG_DECODE_TRNS | c.SPNG_DECODE_GAMMA, c.DecodeFlags)

    # Set PYSPNG_TEST_IMAGE_DIR to inspect the generated PNGs in an external viewer.
    output_dir = os.environ.get('PYSPNG_TEST_IMAGE_DIR')
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))

    def png(color_type, depth, pixels, trns, palette=None):
        # Build a 3x1 PNG directly so the test needs no external images or Pillow.
        data = b'\x89PNG\r\n\x1a\n'
        data += chunk(b'IHDR', struct.pack('>IIBBBBB', 3, 1, depth, color_type, 0, 0, 0))
        if palette is not None:
            data += chunk(b'PLTE', palette)
        data += chunk(b'tRNS', trns)
        # Prefix the pixel row with filter byte 0: store the pixels without filtering.
        data += chunk(b'IDAT', zlib.compress(b'\x00' + pixels))
        data += chunk(b'IEND', b'')
        if output_dir:
            color_name = {0: 'grayscale', 2: 'truecolor', 3: 'palette'}[color_type]
            with open(os.path.join(output_dir, f'trns_{color_name}_{depth}bit.png'), 'wb') as fp:
                fp.write(data)
        return data

    # Three palette colors, addressed by pixel indices 0, 1, and 2.
    palette = bytes([10, 20, 30, 40, 50, 60, 70, 80, 90])
    expected = np.array([[[10, 20, 30, 0], [40, 50, 60, 128], [70, 80, 90, 255]]], dtype=np.uint8)
    # Both rows contain indices 0, 1, 2; the 2-bit row packs them left to right, then pads with 00.
    for depth, pixels in [(8, b'\x00\x01\x02'), (2, bytes([0b00_01_10_00]))]:
        # tRNS gives indices 0 and 1 alpha 0 and 128; omitted index 2 defaults to alpha 255.
        data = png(3, depth, pixels, b'\x00\x80', palette)
        np.testing.assert_array_equal(m.load(data, 'RGBA'), expected)
        opaque = expected.copy()
        opaque[:, :, 3] = 255
        np.testing.assert_array_equal(m.load(data, 'RGBA', flags=m.DecodeFlags(0)), opaque)
        np.testing.assert_array_equal(c.spng_decode_image_bytes(data, c.SPNG_FMT_RGBA8, flags=0), opaque)
        np.testing.assert_array_equal(c.spng_decode_image_bytes(data, c.SPNG_FMT_RGBA8, c.SPNG_DECODE_TRNS), expected)
        np.testing.assert_array_equal(m.load(data, 'RGB'), expected[:, :, :3])
        # Automatic palette output remains RGB, even when the PNG contains tRNS.
        np.testing.assert_array_equal(m.load(data), expected[:, :, :3])

        # Insert gAMA=1.0 after IHDR: enabling correction should brighten RGB without changing alpha.
        gamma_data = data[:33] + chunk(b'gAMA', struct.pack('>I', 100000)) + data[33:]
        np.testing.assert_array_equal(m.load(gamma_data, 'RGBA'), expected)
        corrected = expected.copy()
        corrected[:, :, :3] = ((expected[:, :, :3] / 255.0) ** (1 / 2.2) * 255).astype(np.uint8)
        flags = m.SPNG_DECODE_TRNS | m.SPNG_DECODE_GAMMA
        np.testing.assert_array_equal(m.load(gamma_data, 'RGBA', flags=flags), corrected)
        np.testing.assert_array_equal(c.spng_decode_image_bytes(gamma_data, c.SPNG_FMT_RGBA8, flags), corrected)
        corrected[:, :, 3] = 255
        np.testing.assert_array_equal(m.load(gamma_data, 'RGBA', flags=m.SPNG_DECODE_GAMMA), corrected)

        # Progressive mode would return before filling the array, so reject it and other unsupported bits.
        for flags in [256, 8, 1 << 20, -1]:
            try:
                c.spng_decode_image_bytes(data, c.SPNG_FMT_RGBA8, flags)
            except ValueError as e:
                assert 'unsupported decode flags' in str(e)
            else:
                raise AssertionError(f'Unsupported decode flags accepted: {flags}')

    # For grayscale/RGB, tRNS names one fully transparent color; all other colors are opaque.
    # 0x2a01 and 0x2a02 both become 42 in 8-bit output, but only 0x2a01 should be transparent.
    for depth, key, other in [(8, 42, 43), (16, 0x2a01, 0x2a02)]:
        sample_fmt = '>B' if depth == 8 else '>H'
        value = key if depth == 8 else key >> 8
        other_value = other if depth == 8 else other >> 8
        for color_type, channels in [(0, 1), (2, 3)]:  # Grayscale and truecolor.
            # First and last pixels match the transparent color; the middle pixel does not.
            pixels = b''.join(struct.pack(sample_fmt, v) * channels for v in (key, other, key))
            # Encode the transparent color as one 16-bit value per channel, even for 8-bit PNGs.
            data = png(color_type, depth, pixels, struct.pack('>H', key) * channels)
            expected = np.array([[[value, value, value, 0],
                                  [other_value, other_value, other_value, 255],
                                  [value, value, value, 0]]], dtype=np.uint8)
            np.testing.assert_array_equal(m.load(data, 'RGBA'), expected)
            np.testing.assert_array_equal(m.load(data, 'RGB'), expected[:, :, :3])
            if color_type == 0 and depth == 8:
                np.testing.assert_array_equal(m.load(data, 'LA'), expected[:, :, [0, 3]])


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
    assert 'could not decode ihdr' in str(e)

synthetic_test()
test_image_files()
test_trns()

print ('All tests ok.')
