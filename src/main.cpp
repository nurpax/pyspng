#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "libspng-0.6.1/spng/spng.h"

namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

py::array_t<uint8_t> load_png(py::bytes png_bits) {
    spng_ctx *ctx = spng_ctx_new(0);

    /* Ignore and don't calculate chunk CRC's */
    spng_set_crc_action(ctx, SPNG_CRC_USE, SPNG_CRC_USE);

    /* Set memory usage limits for storing standard and unknown chunks,
       this is important when reading arbitrary files! */
    size_t limit = 1024 * 1024 * 64;
    spng_set_chunk_limits(ctx, limit, limit);

    /* Set source PNG */
    std::string bits = png_bits;
    spng_set_png_buffer(ctx, bits.data(), bits.length());

    struct spng_ihdr ihdr;
    if (spng_get_ihdr(ctx, &ihdr)) {
        return py::array_t<uint8_t>(); // TODO ERRORS
    }

    int w = ihdr.width;
    int h = ihdr.height;
    int c = 3;
    int out_fmt = SPNG_FMT_RGB8;
    size_t out_size;
    if (spng_decoded_image_size(ctx, out_fmt, &out_size)) {
        return py::array_t<uint8_t>(); // TODO ERRORS
    }

    auto* data = new uint8_t[out_size];
    if (spng_decode_image(ctx, data, out_size, out_fmt, 0)) {
        return py::array_t<uint8_t>(); // TODO ERRORS
    }
    spng_ctx_free(ctx);

    py::capsule free_when_done(data, [](void *f) {
        uint8_t* arr = reinterpret_cast<uint8_t*>(f);
        delete[] arr;
    });

    return py::array_t<uint8_t>(
        {h, w, c},              // shape
        {w*c, c, 1},            // C-style contiguous strides for double
        data,                   // the data pointer
        free_when_done          // numpy array references this parent
    );
}

namespace py = pybind11;

PYBIND11_MODULE(pyspng, m) {
    m.def("load_png", &load_png, R"pbdoc(
    Load PNG from a python `bytes` object.  Return as an `np.array`.
    )pbdoc");
#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
