# import numpy as np

# 65546 (64K) memory points or 16384 points. also represents the discrete time points:
SAMPLE_NUM = 256
time_domain = range(0, SAMPLE_NUM)	# for matplotlib representation purposes
N = 9  # number of shape structure points. must be >= 4
    

# 12 bit DAC margin levels. These integers can also be user cinfigurable to match the
# target's requirements, or experiment requirements.
MAX_VAL_DAC = 2047
MIN_VAL_DAC = -2048
RESOLUTION = 20 / 4096	# DAC can out +-10 volts peak to peak when load is Hi-Z
MIN_VAL_VOL = -10
MAX_VAL_VOL = 10



class Chromosome(object):
	"""An individual class that contains the glitch attributes as genes/locuses of a chromosome."""

	def __init__(self):
		self.waveform = None	# glitch waveform
		self.shape_idx = [] # index of points in waveform that can be changed
        self.length = 0     # glitch length
		self.timing = 0		# glitch timing
		self.idle = 3.3		# voltage idle
		
		

	



	