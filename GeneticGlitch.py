from global_constants_and_functions import *
from selection import ElitistGA
from logger import FitnessLoggingGA, PopulationLoggingGA
from individual import Chromosome
from score_chromosome import score_chromosome

class GeneticGlitch(FitnessLoggingGA, PopulationLoggingGA, ElitistGA):
    def __init__(self, config={}):
        """
        Initializes genetic algorithm to find optimal voltage glitch.
        :param config: configuration dictionary
        """
        super().__init__(config)
        self.chromosome_length = self.config.setdefault("chromosome_length", N)

    def chromosome_str(self, chromosome):
        return str(chromosome)

    def create(self):
        return Chromosome(length=self.chromosome_length)

    def score(self, chromosome):
        """This should send a "score" command to the arduino, that runs a several amount of glitches of the current
        waveform and returns the average score based on the reward engineered.
        :param chromosome:
        :return:score
        """
        return score_chromosome(chromosome)

if __name__ == "__main__":
    g = GeneticGlitch()
    g.seed()
