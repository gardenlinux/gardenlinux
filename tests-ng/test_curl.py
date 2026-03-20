from ctypes import CDLL, c_int, c_void_p

import pytest

def test_init_libcurl():
    libcurl = CDLL("libcurl.so.4")
    assert libcurl.curl_global_init() == 0, "Coudn't initializ libcurl"
