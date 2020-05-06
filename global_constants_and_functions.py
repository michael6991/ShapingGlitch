# Global imports:
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from copy import deepcopy
import random
import uuid

# 65546 (64K) memory points or 16384 points. also represents the discrete time points:
SAMPLE_NUM = 16384
time_domain = range(0, SAMPLE_NUM)  # for matplotlib representation purposes
N = 8  # number of shape structure points. must be >= 4

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

config = {}
config.setdefault("population_size", 50)
config.setdefault("crossover_prob", 0.8)
config.setdefault("max_iterations", 100)
config.setdefault("remove_worst_num", 1)
config.setdefault("add_random_num", 2)  # It is recommended to have add_random_num > remove_worst_num,
                                        # to make sure atleast one new agent is evaluated every generation
config.setdefault("elitism_pct", 0.02)
config.setdefault("log_best_chromosome", True)
config.setdefault("best_chromosome_file", "best_chromosome_log.txt")
config.setdefault("chromosome_length_initial", N)
config.setdefault("mutation_y_prob", 0.1)
config.setdefault("mutation_y_size", 0.25)
config.setdefault("mutation_reorder_prob", 0.01)
config.setdefault("mutation_freq_prob", 0.1)
config.setdefault("mutation_freq_size", MIN_FREQ)
config.setdefault("mutation_add_or_remove_prob", 0.01)
config.setdefault("mutation_random_parent_crossover_prob", 0.01)
config.setdefault("threshold", 0.0001)
config.setdefault("lookback", 80)


def convert_int_to_comp2_binary_string(val: int, bits: int):
    newnum = val & ((1 << bits) - 1)
    return ("{0:0" + str(bits) + "b}").format(newnum)


def convert_int_to_comp2_ascii(val: int, bytes_num: int):
    len_bits = bytes_num << 3  # bytes * 8
    newnum = val & ((1 << len_bits) - 1)
    return newnum.to_bytes(bytes_num, byteorder='big')
