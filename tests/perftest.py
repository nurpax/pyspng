
import io
import time
import numpy as np
import PIL.Image

import pyspng

def decode_benchmark(title='', content='noise', width=1024, height=1024, compress_level=0, loader='spng', num_repeats=10, num_calls=10):
    if content == 'noise':
        img = np.random.randint(0, 256, size=[height,width,3], dtype=np.uint8)
    if content == 'gradient':
        x, y, _c = np.mgrid[:height, :width, :1]
        img = np.concatenate([y * 255 / height, x * 255 / width, x * 0], axis=2).astype(np.uint8)

    stream = io.BytesIO()
    PIL.Image.fromarray(img, 'RGB').save(stream, format='png', compress_level=compress_level)
    bytes = stream.getvalue()

    lowest_ms = float('inf')
    for _repeat_idx in range(num_repeats):
        start_time = time.time()
        for _call_idx in range(num_calls):
            if loader == 'pil':
                out = np.asarray(PIL.Image.open(io.BytesIO(bytes)))
            if loader == 'spng':
                out = pyspng.load(bytes)
        cur_ms = (time.time() - start_time) * 1e3
        lowest_ms = min(lowest_ms, cur_ms)
    print(f'{title}  {lowest_ms:.2f}ms')
    assert np.all(out == img)

def encode_benchmark(title='', content='noise', width=1024, height=1024, compress_level=0, loader='spng', num_repeats=10, num_calls=10):
    if content == 'noise':
        img = np.random.randint(0, 256, size=[height,width,3], dtype=np.uint8)
    if content == 'gradient':
        x, y, _c = np.mgrid[:height, :width, :1]
        img = np.concatenate([y * 255 / height, x * 255 / width, x * 0], axis=2).astype(np.uint8)

    lowest_ms = float('inf')
    for _repeat_idx in range(num_repeats):
        start_time = time.time()
        for _call_idx in range(num_calls):
            if loader == 'pil':
                stream = io.BytesIO()
                PIL.Image.fromarray(img, 'RGB').save(stream, format='png', compress_level=compress_level)
            if loader == 'spng':
                pyspng.encode(img, compress_level=compress_level)
        cur_ms = (time.time() - start_time) * 1e3
        lowest_ms = min(lowest_ms, cur_ms)
    print(f'{title}  {lowest_ms:.2f}ms')

if __name__ == "__main__":
    decode_benchmark('d: pil  compressed   noise   ', content='noise',    compress_level=9, loader='pil')
    decode_benchmark('d: pil  compressed   gradient', content='gradient', compress_level=9, loader='pil')
    decode_benchmark('d: pil  uncompressed noise   ', content='noise',    compress_level=0, loader='pil')
    decode_benchmark('d: pil  uncompressed gradient', content='gradient', compress_level=0, loader='pil')
    decode_benchmark('d: spng compressed   noise   ', content='noise',    compress_level=9, loader='spng')
    decode_benchmark('d: spng compressed   gradient', content='gradient', compress_level=9, loader='spng')
    decode_benchmark('d: spng uncompressed noise   ', content='noise',    compress_level=0, loader='spng')
    decode_benchmark('d: spng uncompressed gradient', content='gradient', compress_level=0, loader='spng')

    encode_benchmark('e: pil  compressed   noise   ', content='noise',    compress_level=9, loader='pil')
    encode_benchmark('e: pil  compressed   gradient', content='gradient', compress_level=9, loader='pil')
    encode_benchmark('e: pil  uncompressed noise   ', content='noise',    compress_level=0, loader='pil')
    encode_benchmark('e: pil  uncompressed gradient', content='gradient', compress_level=0, loader='pil')
    encode_benchmark('e: spng compressed   noise   ', content='noise',    compress_level=9, loader='spng')
    encode_benchmark('e: spng compressed   gradient', content='gradient', compress_level=9, loader='spng')
    encode_benchmark('e: spng uncompressed noise   ', content='noise',    compress_level=0, loader='spng')
    encode_benchmark('e: spng uncompressed gradient', content='gradient', compress_level=0, loader='spng')
