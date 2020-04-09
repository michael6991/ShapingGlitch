import random, math
import matplotlib.pyplot as plt
import shapes

# import os
# import sys
# sys.path.insert(0, os.path.abspath('..'))


import individual#, crossover, mutation, FitnessLoggingGA, ProportionateGA, ElitistGA

class TestProblem():
    """Genetic solution to the 0/1 Knapsack Problem."""

    def __init__(self):
        """Initialize a 0/1 knapsack solver.

        Raises:
            AttributeError: If ``items`` is not in the configuration dict.
        """
        super(self.__class__, self).__init__()


    def create(self):
        """
        Generates a chromosome/individual. this method overrides the create method in the basic class.
        A chromosome consists of:
        - waveform vector of glitch
        - length of glitch
        - voltage idle
        - timing of the glitch
        """
        chromo = individual.Chromosome()

        
        # initial random glitch length. must be less than SAMPLE_NUM
        chromo.length = random.choice(range(100, 250, 10))
        
        # get a random low voltage
        low = random.uniform(individual.MIN_VOLT, individual.MAX_VOLT)
        # get a random high voltage
        high = random.uniform(low + random.random(), individual.MAX_VOLT)
        print("low volt: %f" % low + "   high volt: %f" % high)
        
        
        '''
        
        # insert initial idle voltage, before the glitch shape
        for i in range(0, chromo.timing):
            chromo.waveform[i] = chromo.idle

        # insert a random voltage point inside the glitch length
        for i in range(chromo.timing, chromo.timing + chromo.length):
            chromo.waveform[i] = random.randint(individual.MIN_VAL_VOL, individual.MAX_VAL_VOL)

        # pad the rest of the waveform with idle voltage after the glitch shape
        for i in range(chromo.timing + chromo.length, individual.SAMPLE_NUM):
            chromo.waveform[i] = chromo.idle
        '''
        
        # choose a random initial shape
        shape = random.choice(shapes.basic_shapes)
        
        chromo.waveform = shapes.choose_shape(shape, 
                                              chromo.length,
                                              individual.N,
                                              high,
                                              low)
        

        
        
        return chromo



    def chromosome_str(self, chromosome):
        print("Chromosome genes:")
        print("\t\t- length %d" % chromosome.length)
        print("\t\t- timing %d" % chromosome.timing)
        print("\t\t- voltage idle %f" % chromosome.idle)
        print("waveform")
        print(chromosome.waveform)

        t = [chromosome.waveform[i][0] for i in range(0, len(chromosome.waveform))]
        v = [chromosome.waveform[i][1] for i in range(0, len(chromosome.waveform))]
        plt.figure()
        plt.plot(t, v)
        plt.grid(True)
        plt.show()

        
        
test = TestProblem()
test.chromosome_str(test.create())
print("done")
