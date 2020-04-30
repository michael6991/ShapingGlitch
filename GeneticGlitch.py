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
        self.mutation_size = self.config.setdefault("mutation_size", 0.75)

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
        """
        """
        parent1 = self.select()
        parent2 = parent1
        search_counter_max = 10     # may be change to:  counter_max = population_size / 4.
                                    # at least it has a parameter involved, instead of a plain number.
                                    # i don't know...
        search_counter = 0
        while self.check_chromosomes_equality(parent1, parent2):
            parent2 = self.select()
            search_counter += 1
            if search_counter > search_counter_max:
                parent2 = Chromosome()
        return self.uniform_waveform_crossover(parent1, parent2)

    @staticmethod
    def check_chromosomes_equality(parent1, parent2):
        """
        Check whether two chromosomes have equal waveform coordinates
        :return:True or False
        """
        if parent1.length < parent2.length:
            tup = parent1, parent2
        else:
            tup = parent2, parent1
        return np.isin(tup[0].coordinates, tup[1].coordinates).all()

    @staticmethod
    def uniform_waveform_crossover(parent1, parent2):
        """ Perform uniform crossover on out waveform chromosomes.
        
        the code is quite messy. would be great if additional description
        will be added here.

        note:
            The difference between shallow and deep copying is only relevant for
            compound objects (objects that contain other objects, like lists or
            class instances).
    
            -   A shallow copy constructs a new compound object and then (to the
                extent possible) inserts *the same objects* into it that the
                original contains.
    
            -   A deep copy constructs a new compound object and then, recursively,
                inserts *copies* into it of the objects found in the original.

        Returns:
            List[Chromosome]: Two new chromosomes descended from the given parents.
        """
        if parent1.length < parent2.length:
            tup = parent1, parent2
        else:
            tup = parent2, parent1
        child1 = deepcopy(tup[0])
        child2 = deepcopy(tup[1])
        indices_from_long_parent = np.sort(np.random.permutation(tup[1].length)[:tup[0].length])
        for locus in range(tup[0].length):
            if random.randint(0, 1) == 1:
                child1.coordinates[locus] = tup[1].coordinates[indices_from_long_parent[locus]]
                child2.coordinates[indices_from_long_parent[locus]] = tup[0].coordinates[locus]
        child1.sort_coordinates()
        child2.sort_coordinates()
        freq_part_crossover = random.random()
        child1.freq = freq_part_crossover * tup[0].freq + (1 - freq_part_crossover) * tup[1].freq
        child2.freq = freq_part_crossover * tup[1].freq + (1 - freq_part_crossover) * tup[0].freq
        return [child1, child2]

    def mutate(self, chromosome):
        """
        with probability mutation_prob:
        1) Change a random y value by a random value
        2) add a random point
        Also always change id.
        :param chromosome:
        :return:
        """
        if random.random() < self.mutation_prob:
            ind = random.choice(range(chromosome.length))
            amount_to_change = (- 0.5 + random.random()) * self.mutation_size
            chromosome.coordinates[ind, 1] += amount_to_change
        chromosome.id = uuid.uuid4()                        #  why ???, the initial id is unique already...
        return chromosome

    def pre_generate(self):
        """
        Before applying the GA selection, crossover, and mutation
        methods on a certain generation, make sure that every chromosome
        is unique and differs from others - by adding random noise to the
        the attributes of the "similar" chromosome.
        This function preserves "better" chromosomes with good solution attributes
        and expands the solution space , so that GA won't converge around
        a ot optimal solution.

        Will overwrite pre_generate method in base class.
        """
        super().pre_generate()
        for chromosome in self.population:
            chromosome.sort_coordinates()
        for chromosome1 in self.population:
            for chromosome2 in self.population:
                if chromosome1.id != chromosome2.id and \
                        chromosome1.length == chromosome2.length and \
                        self.check_chromosomes_equality(chromosome1, chromosome2):
                    chromosome2.add_noise()  # if we want to keep attributes of good solutions that were duplicated


if __name__ == "__main__":
    from score_chromosome import v_pulse_shape

    g = GeneticGlitch()
    solution = g.solve()
    # plot
    x_samples, y_samples = solution.interpolate_coordinates()
    fig, ax = plt.subplots()
    ax.plot(np.arange(SAMPLE_NUM) / (SAMPLE_NUM - 1), v_pulse_shape(0.6, 0.6, 0.6), c='g')
    ax.plot(x_samples, y_samples, c='b')
    ax.scatter(solution.coordinates[:, 0], solution.coordinates[:, 1], c='r')
    ax.legend(['Target waveform', 'Result waveform', 'Chromosome coordinates'])
    ax.grid()
    plt.show()

