# Global imports:
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from copy import deepcopy
import random

# 65546 (64K) memory points or 16384 points. also represents the discrete time points:
SAMPLE_NUM = 16384
time_domain = range(0, SAMPLE_NUM)  # for matplotlib representation purposes
N = 9  # number of shape structure points. must be >= 4

# 12 bit DAC margin levels. These integers can also be user cinfigurable to match the
# target's requirements, or experiment requirements.
MAX_DAC_INT = 2047
MIN_DAC_INT = -2047
RESOLUTION = 20 / 4096  # DAC can out +-10 volts peak to peak when load is Hi-Z
MIN_DAC_VOL = -10
MAX_DAC_VOL = 10
# OFFSET = 0


# # Targets voltage limitations in [V]
# MIN_VOLT = 0
# MAX_VOLT = 5.5
MAX_FREQ = 25e6
MIN_FREQ = 1e6  # not an actual limit but seems reasonable


def convert_int_to_comp2_binary_string(val: int, bits: int):
    newnum = val & ((1 << bits) - 1)
    return ("{0:0" + str(bits) + "b}").format(newnum)


def convert_int_to_comp2_ascii(val: int, bytes: int):
    len = bytes << 3  # bytes * 8
    newnum = val & ((1 << len) - 1)
    return newnum.to_bytes(bytes, byteorder='big')
