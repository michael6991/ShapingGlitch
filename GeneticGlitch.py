from global_constants_and_functions import *
from selection import ElitistGA, ScalingProportionateGA
from logger import FitnessLoggingGA, PopulationLoggingGA
from behavior import FinishWhenSlowGA
from individual import Chromosome
from score_chromosome import score_chromosome


class GeneticGlitch(FitnessLoggingGA, PopulationLoggingGA, ElitistGA, ScalingProportionateGA  # FinishWhenSlowGA
                    ):
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

    def crossover(self):
        parent1 = self.select()
        parent2 = parent1
        while self.check_chromosomes_equality(parent1, parent2):
            parent2 = self.select()
        return self.uniform_waveform_crossover(parent1, parent2)

    @staticmethod
    def check_chromosomes_equality(parent1, parent2):
        if parent1.length < parent2.length:
            tup = parent1, parent2
        else:
            tup = parent2, parent1
        return np.isin(tup[0].coordinates, tup[1].coordinates).all()

    @staticmethod
    def uniform_waveform_crossover(parent1, parent2):
        """ Perform uniform crossover on out waveform chromosomes.
        Returns:
            List[Chromosome]: Two new chromosomes descended from the given parents.
        """
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
        for locus in range(min(parent1.length, parent2.length)):
            if random.randint(0, 1) == 1:
                child1.coordinates[locus] = parent2.coordinates[locus]
                child2.coordinates[locus] = parent1.coordinates[locus]
        child1.sort_coordinates()
        child2.sort_coordinates()
        freq_part_crossover = random.random()
        child1.freq = freq_part_crossover * parent1.freq + (1 - freq_part_crossover) * parent2.freq
        child2.freq = freq_part_crossover * parent2.freq + (1 - freq_part_crossover) * parent1.freq
        return [child1, child2]

    def mutate(self, chromosome):
        """
        Swap 2 neighboring y values with some probability.
        Also always change id.
        :param chromosome:
        :return:
        """
        if random.random() < self.mutation_prob:
            ind = random.choice(range(chromosome.length - 1))
            tmp_to_swap = chromosome.coordinates[ind, 1]
            chromosome.coordinates[ind, 1] = chromosome.coordinates[ind + 1, 1]
            chromosome.coordinates[ind + 1, 1] = tmp_to_swap
        chromosome.id = uuid.uuid4()
        return chromosome

    def pre_generate(self):
        super().pre_generate()
        for chromosome in self.population:
            chromosome.sort_coordinates()
        for chromosome1 in self.population:
            for chromosome2 in self.population:
                if chromosome1.id != chromosome2.id and \
                        chromosome1.length == chromosome2.length and \
                        self.check_chromosomes_equality(chromosome1, chromosome2):
                    chromosome2.coordinates = chromosome2.calculate_random_coordinates(self.chromosome_length)
                    chromosome1.freq = np.mean([chromosome1.freq, chromosome2.freq])


if __name__ == "__main__":
    g = GeneticGlitch()
    solution = g.solve()
    solution.plot_waveform_uncut()
