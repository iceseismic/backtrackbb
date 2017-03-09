# -*- coding: utf8 -*-
import os
import ctypes
from numpy.ctypeslib import ndpointer
import numpy as np


libpath = os.path.join(os.path.dirname(__file__), 'lib', 'lib_rec_cc.so')
lib_rec_cc = ctypes.CDLL(libpath)

lib_rec_cc._Gaussian1D.argtypes = [
        ndpointer(dtype=np.float64),  # signal
        ctypes.c_int,                 # npts
        ctypes.c_double               # sigma
        ]
lib_rec_cc._Gaussian1D.restype = ctypes.c_void_p


def recursive_gauss_filter(signal, sigma):
    filt_signal = np.array(signal, dtype=np.float64)
    lib_rec_cc._Gaussian1D(filt_signal, filt_signal.size, sigma)
    return filt_signal


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    signal = np.zeros(1001)
    signal[500] = 1
    filt_signal = recursive_gauss_filter(signal, 10)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(signal)
    ax.plot(filt_signal/max(filt_signal))
    plt.show()
