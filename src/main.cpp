#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "spng/spng.h"

namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

py::array_t<uint8_t> load_png(py::bytes png_bits) {
    std::unique_ptr<spng_ctx, void(*)(spng_ctx*)> ctx(spng_ctx_new(0),  spng_ctx_free);

    /* Ignore and don't calculate chunk CRC's */
    spng_set_crc_action(ctx.get(), SPNG_CRC_USE, SPNG_CRC_USE);

    /* Set memory usage limits for storing standard and unknown chunks,
       this is important when reading arbitrary files! */
    size_t limit = 1024 * 1024 * 64;
    spng_set_chunk_limits(ctx.get(), limit, limit);

    /* Set source PNG */
    std::string bits = png_bits;
    spng_set_png_buffer(ctx.get(), bits.data(), bits.length());

    struct spng_ihdr ihdr;
    if (spng_get_ihdr(ctx.get(), &ihdr) != SPNG_OK) {
        throw std::runtime_error("pyspng: could not decode image size");
    }

    int w = ihdr.width;
    int h = ihdr.height;
    int c = 3;
    int out_fmt = SPNG_FMT_RGB8;
    size_t out_size;
    if (spng_decoded_image_size(ctx.get(), out_fmt, &out_size) != SPNG_OK) {
        throw std::runtime_error("pyspng: could not decode image size");
    }

    auto* data = new uint8_t[out_size];
    if (spng_decode_image(ctx.get(), data, out_size, out_fmt, 0) != SPNG_OK) {
        delete[] data;
        throw std::runtime_error("pyspng: could not decode image");
    }

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

PYBIND11_MODULE(pyspng, m) {
    m.doc() = R"pbdoc(
        pyspng API reference
        --------------------

        .. currentmodule:: pyspng

        .. autosummary::
           :toctree: _generate

           load_png
    )pbdoc";

    m.def("load_png", &load_png, py::arg("data"), R"pbdoc(
        Load PNG from a python `bytes` object..

        Args:
            data (bytes): PNG file contents in memory.
        Returns:
            numpy.ndarray: Image pixel data in shape (height,width,3).

    )pbdoc");
#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
