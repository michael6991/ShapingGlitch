from global_constants_and_functions import *
from selection import ElitistGA, ProportionateGA, ScalingProportionateGA
from logger import FitnessLoggingGA, PopulationLoggingGA, BestChromosomeLoggingGA
from behavior import FinishWhenSlowGA
from individual import Chromosome
from score_chromosome import score_chromosome


class GeneticGlitch(ElitistGA, ScalingProportionateGA, FinishWhenSlowGA, BestChromosomeLoggingGA
                    ):
    def __init__(self, config={}):
        """
        Initializes genetic algorithm to find optimal voltage glitch.
        :param config: configuration dictionary
        """
        super().__init__(config)
        self.chromosome_length_initial = self.config.setdefault("chromosome_length", N)
        self.mutation_y_prob = self.config.setdefault("mutation_y_prob", 0.9)
        self.mutation_y_size = self.config.setdefault("mutation_y_size", 0.3)
        self.mutation_reorder_prob = self.config.setdefault("mutation_reorder_prob", 0.05)
        self.mutation_freq_prob = self.config.setdefault("mutation_freq_prob", 0.05)
        self.mutation_freq_size = self.config.setdefault("mutation_freq_size", MIN_FREQ)
        self.mutation_add_or_remove_prob = self.config.setdefault("mutation_add_or_remove_prob", 0.05)
        self.mutation_random_parent_crossover_prob = self.config.setdefault("mutation_random_parent_crossover_prob",
                                                                            0.05)

    def chromosome_str(self, chromosome):
        return str(chromosome)

    def create(self):
        return Chromosome(length=self.chromosome_length_initial)

    def score(self, chromosome):
        """This should send a "score" command to the arduino, that runs a several amount of glitches of the current
        waveform and returns the average score based on the reward engineered.
        :param chromosome:
        :return:score
        """
        return score_chromosome(chromosome)

    def generate(self):
        """Create and assign a new generation as the population."""
        while len(self.next_generation) < self.population_size - self.replace_worst_num:
            if self.random.random() < self.crossover_prob:
                children = self.crossover()
            else:
                children = [self.select() for _ in
                            range(0, self.num_cx_children)]

            for child in children:
                if len(self.next_generation) >= self.population_size - self.replace_worst_num:
                    break

                child = self.mutate(child)
                self.next_generation.append(child)

        for _ in range(self.replace_worst_num):
            self.next_generation.append(self.create())

    def crossover(self):
        """
        Select 2 distinct parents to perform crossover on.
        If no distinct parents can be chosen, create a random second parent.
        """
        parent1 = self.select()
        parent2 = parent1
        search_counter_max = np.ceil(self.population_size / 2)
        search_counter = 0
        while parent1.id == parent2.id:
            parent2 = self.select()
            search_counter += 1
            if search_counter > search_counter_max:
                parent2 = self.create()
        return self.uniform_waveform_crossover(parent1, parent2)

    @staticmethod
    def uniform_waveform_crossover(parent1, parent2):
        """ Perform uniform crossover on two waveform chromosomes.

        Returns:
            List[Chromosome]: Two new chromosomes descended from the given parents.
        """
        # Order chromosomes by length, shorter first
        if parent1.length < parent2.length:
            tup = parent1, parent2
        else:
            tup = parent2, parent1
        # Create children
        child1 = tup[0].make_copy()
        child2 = tup[1].make_copy()
        # Choose indices from long parent to crossover with short parent
        indices_from_long_parent = np.sort(np.random.permutation(tup[1].length)[:tup[0].length])
        # Perform uniform crossover with 50% chance, without adding points that are already in a chromosome:
        for locus in range(tup[0].length):
            if random.randint(0, 1) == 1:
                if not child1.is_x_in_chromosome(tup[1].coordinates[indices_from_long_parent[locus]]):
                    child1.coordinates[locus] = tup[1].coordinates[indices_from_long_parent[locus]]
                if not child2.is_x_in_chromosome(tup[0].coordinates[locus]):
                    child2.coordinates[indices_from_long_parent[locus]] = tup[0].coordinates[locus]
        # Sort coordinates in case they got messed up
        child1.sort_coordinates()
        child2.sort_coordinates()
        # Perform frequency crossover
        freq_part_crossover = random.random()
        child1.freq = freq_part_crossover * tup[0].freq + (1 - freq_part_crossover) * tup[1].freq
        child2.freq = freq_part_crossover * tup[1].freq + (1 - freq_part_crossover) * tup[0].freq
        return [child1, child2]

    def mutate(self, chromosome):
        """
        Possible mutations:
        1) changing y value of random point
        2) swapping 2 points'  y values.
        3) removing or adding random point
        4) adding noise to frequency
        Also changes ID.
        :param chromosome:
        :return:
        """
        # random y coordinate mutation:
        if random.random() < self.mutation_y_prob:
            ind = random.choice(range(chromosome.length))
            amount_to_change = np.random.randn() * self.mutation_y_size
            chromosome.coordinates[ind, 1] += amount_to_change
        # swap mutation
        if random.random() < self.mutation_reorder_prob and chromosome.length > 1:
            ind = random.choice(range(chromosome.length - 1))
            tmp_to_swap = chromosome.coordinates[ind, 1]
            chromosome.coordinates[ind, 1] = chromosome.coordinates[ind + 1, 1]
            chromosome.coordinates[ind + 1, 1] = tmp_to_swap
        # remove or add point mutation
        if random.random() < self.mutation_add_or_remove_prob:
            # remove random point
            if random.randint(0, 1) == 0:
                ind = random.choice(range(chromosome.length))
                chromosome.remove_point(ind)
            # add random point
            else:
                chromosome.add_random_point()
        # frequency mutation
        if random.random() < self.mutation_freq_prob:
            chromosome.freq += self.mutation_freq_size * np.random.randn()
        # random parent crossover mutation
        if random.random() < self.mutation_random_parent_crossover_prob:
            random_parent = self.create()
            children = self.uniform_waveform_crossover(chromosome, random_parent)
            chromosome = children[random.randint(0, 1)]
        chromosome.generate_new_id()
        return chromosome

    def pre_generate(self):
        """
        Before applying the GA selection, crossover, and mutation
        methods on a certain generation, make sure that every chromosome
        is unique and differs from others - by adding random noise to the
        the attributes of the "similar" chromosome.
        This function preserves "better" chromosomes with good solution attributes
        and expands the solution space , so that the GA won't converge around
        a suboptimal solution.
        """
        super().pre_generate()
        for chromosome1 in self.population:
            for chromosome2 in self.population:
                # make sure they aren't the same chromosome chosen twice.
                if chromosome1.id != chromosome2.id and \
                        chromosome1.length == chromosome2.length and \
                        (chromosome1.coordinates == chromosome2.coordinates).all():
                    chromosome2.add_noise()  # if we want to keep attributes of good solutions that were duplicated

    def best(self):
        """
        Return best chromosome ever.
        :return:
        """
        print("Returning best chromosome of iteration {}".format(self.iteration_of_best_fitness))
        return self.best_chromosome_of_all


if __name__ == "__main__":
    from score_chromosome import v_pulse_shape

    g = GeneticGlitch(config)
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
