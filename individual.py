# import numpy as np

# 65546 (64K) memory points or 16384 points. also represents the discrete time points:
SAMPLE_NUM = 512
time_domain = range(0, SAMPLE_NUM)    # for matplotlib representation purposes
N = 9  # number of shape structure points. must be >= 4
    

# 12 bit DAC margin levels. These integers can also be user cinfigurable to match the
# target's requirements, or experiment requirements.
MAX_DAC_INT = 2047
MIN_DAC_INT = -2048
RESOLUTION = 20 / 4096    # DAC can out +-10 volts peak to peak when load is Hi-Z
MIN_DAC_VOL = -10
MAX_DAC_VOL = 10


# Targets voltage limitations in [V]
MIN_VOLT = 0
MAX_VOLT = 5.5


class Chromosome(object):
    """An individual class that contains the glitch attributes as genes/locuses of a chromosome."""

    def __init__(self):
        self.waveform = None
        self.length = 0
        self.timing = 0
        self.idle = 5.0
        