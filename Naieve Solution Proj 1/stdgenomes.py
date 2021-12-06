"""This module contains some standard genome types.

Too use, see ga.py
"""

import random

class BaseGenome:
    """Base class for building genomes. Cannot be used on its own!

    You do not have to inherit from this class to create a new genome class,
    just make sure you have a spawn and a fresh method with the correct
    interface.

    BaseGenome has a standard spawn method for randomly selecting which
    evolutionary operator to use each time a new genome is created.
    """
    def __init__(self, spawn_chances):
        """Constructor of BaseGenome

        @param spawn_chances: An iterable of tuples with
        (evolutionary method, chance). If you have three evolutionary
        methods: mutate, copy and crossover, and supply the following
        list [(MyGenome.mutate, 3), (MyGenome.copy, 1), (MyGenome.crossover, 3)]
        Then copy will have 1 chance in 7 of being selected, mutate will have 3
        chances in 7 and crossover will also have 3 in 7.
        """
        self.spawn_chances = spawn_chances
        self.total_target = sum(chance for _, chance in spawn_chances)
        self.partner = None

    def spawn(self, partner):
        """Use yourself and partner to create a child genome. Pick one of the
        evolutionary methods from spawn_chances randomly (using weights from
        spawn_chances) and apply it.

        @param partner: The other genome that can be involved in the spawning.
        """
        self.partner = partner
        rnd = random.randrange(self.total_target)
        for spawn_fun, chance in self.spawn_chances:
            if rnd <= chance:
                child = spawn_fun(self)
                break
            rnd -= chance

        del self.partner # prevent memory leak
        return child

    def fresh(self):
        """Construct and return a freshly randomized genome.
        """
        pass

class FloatGenome(BaseGenome):
    """FloatGenome is a standard genome - a vector of floats.

    Per default the floats are randomized in the [0, 1] range, but
    this can be changed in the constructor. However, you do not have a guarantee
    that the floats will stay in that range after mutation. If, for example,
    negative floats are forbidden in your application you have to take care of
    this in the fitness function.
    """
    def __init__(self, initial, init_limits=(0, 1),
                 spawn_chances=None, resolution=0.001):
        """FloatGenome constructor.

        @param initial: Initial is either a vector containing the genome
        of this object or a length of a vector, that should be filled with
        random values from the init_limits range.

        @param init_limits: A tuple of the lower and upper limits for initial
        randomization. There is no guarantee that the values stay in this range
        after mutation. Per default the range is [0, 1].

        @param spawn_chances: An iterable that is passed on to BaseGenome (see
        that constructor for more information). The evolutionary operators
        of this class is copy, fresh, crossover, swap, small_mutate,
        medium_mutate and big_mutate.

        @param resolution: A rough estimate of the lowest interesting resolution
        for the genes. this is used by small_mutate to make small adjustments.
        Per default it is 0.001.
        """
        self.init_limits = init_limits
        if type(initial) is list:
            self.genes = initial[:]
        else:
            self.genes = [self.new_val() for _ in range(initial)]

        self.resolution = resolution

        if not spawn_chances:
            spawn_chances = ((FloatGenome.fresh, 1),
                             (FloatGenome.copy, 1),
                             (FloatGenome.crossover, 3),
                             (FloatGenome.big_mutate, 1),
                             (FloatGenome.medium_mutate, 3),
                             (FloatGenome.small_mutate, 2))

        BaseGenome.__init__(self, spawn_chances)

    def fresh(self):
        """Construct and return a freshly randomized genome.

        Evolutionary operator.
        """
        return FloatGenome([self.new_val() for _ in self.genes],
                           self.init_limits, self.spawn_chances,
                           self.resolution)

    def new_val(self):
        """Return a new random value in the init_limits range.
        """
        scale = self.init_limits[1] - self.init_limits[0]
        return random.random() * scale + self.init_limits[0]

    def crossover(self):
        """Use genes from both parents to create a new child.

        Evolutionary operator.
        """
        child = self.copy()
        pt1 = random.randrange(len(self.genes))
        pt2 = random.randrange(len(self.genes) - pt1) + pt1
        child.genes[pt1:pt2] = self.partner.genes[pt1:pt2]
        return child

    def swap(self):
        """Swap two values randomly in the vector. Not always a meaningful
        operator. Per default it is switched off.

        Evolutionary operator.
        """
        child = self.copy()
        i = random.randrange(len(child.genes))
        j = random.randrange(len(child.genes))
        child.genes[i], child.genes[j] = child.genes[j], child.genes[i]
        return child

    def mutate(self, val):
        """Add val to a random gene.
        """
        i = random.randrange(len(self.genes))
        self.genes[i] += val

    def small_mutate(self):
        """Make a small mutation to a random gene.

        The size of the mutation is determined by the resolution parameter
        in the constructor.

        Evolutionary operator.
        """
        child = self.copy()
        child.mutate((random.random() - 0.5) * 10 * self.resolution)
        return child

    def big_mutate(self):
        """Completely replace a random gene with a new random value from
        the init_limits range.

        Evolutionary operator.
        """
        child = self.copy()
        child.mutate(self.new_val())
        return child

    def medium_mutate(self):
        """Make a gaussian mutation to a random gene.

        Larger values get a larger standard deviation to the mutations.
        The standard deviation is a fifth of the value of the gene, but no
        smaller than the resolution of small_mutate.

        Evolutionary operator.
        """
        child = self.copy()
        i = random.randrange(len(self.genes))
        gene = child.genes[i]
        child.genes[i] = random.gauss(gene, max(abs(gene) / 5, self.resolution))
        return child

    def copy(self):
        """Return a copy of self.

        Evolutionary operator.
        """
        return FloatGenome(self.genes, self.init_limits, self.spawn_chances,
                           self.resolution)


class PermutateGenome(BaseGenome):
    """PermutateGenome is a standard genome for representing a vector
    of values, where the solution is known to be a permutation of those
    values.

    Sometimes it can be best for the evolutionary process to use an L{EnumGenome},
    even though you know that the final solution must be a permutation of
    certain values, but often it is more efficient to use this class.

    See also the Sudoku example.
    """
    def __init__(self, initial, spawn_chances=None):
        """Constructor for PermutateGenome.

        @param initial: Copy the genome from this vector.

        @param spawn_chances: An iterable that is passed on to BaseGenome (see
        that constructor for more information). The evolutionary operators
        of this class is copy, fresh, crossover and swap.
        """
        self.genes = initial[:]

        if not spawn_chances:
            spawn_chances = ((PermutateGenome.copy, 1),
                             (PermutateGenome.fresh, 1),
                             (PermutateGenome.crossover, 2),
                             (PermutateGenome.swap, 6))

        BaseGenome.__init__(self, spawn_chances)

    def copy(self, genes=None):
        """Return a copy of self.

        Evolutionary operator.
        """
        if not genes:
            genes = self.genes
        return PermutateGenome(genes, self.spawn_chances)

    def fresh(self):
        """Construct and return a freshly randomized genome, by
        shuffling the original.

        Evolutionary operator.
        """
        child = self.copy()
        random.shuffle(child.genes)
        return child

    def swap(self):
        """Swap two values randomly in the vector. A key operator in a
        PermutateGenome.

        Evolutionary operator.
        """
        child = self.copy()
        i = random.randrange(len(child.genes))
        j = random.randrange(len(child.genes))
        child.genes[i], child.genes[j] = child.genes[j], child.genes[i]
        return child

    def crossover(self):
        """Use genes from both parents to create a new child.

        The result is guaranteed to be a permutation of the
        original vector.

        Evolutionary operator.
        """
        genes1 = self.genes[:]
        genes2 = self.partner.genes[:]

        result = []
        i = 0
        conflicts = []
        while i < len(genes1):
            if genes1[i] == genes2[i]:
                result.append(genes1[i])
                genes1.pop(i)
                genes2.pop(i)
            else:
                conflicts.append(len(result))
                result.append(None)
                i += 1

        for i in conflicts:
            if random.random() < 0.5:
                result[i] = genes1[0]
                genes2.remove(genes1.pop(0))
            else:
                result[i] = genes2[0]
                genes1.remove(genes2.pop(0))

        return self.copy(result)


class EnumGenome(BaseGenome):
    """EnumGenome is a standard genome for representing a problem with a
    solution that is known to be a vector of a discrete number of objects.
    For example a set of integers.
    """
    def __init__(self, initial, goodset, spawn_chances=None):
        """Constructor for EnumGenome.

        @param initial: This is either a vector containing the genome
        of this object or a length of a vector, that should be filled with
        random objects from the goodset.

        @param goodset: The set (any non-empty sequence) of objects that can
        be used.

        @param spawn_chances: An iterable that is passed on to BaseGenome (see
        that constructor for more information). The evolutionary operators
        of this class is copy, fresh, crossover and mutate.
        """
        self.goodset = goodset

        if type(initial) is list:
            self.genes = initial[:]
        else:
            self.genes = self.fresh_genes(initial)

        if not spawn_chances:
            spawn_chances = ((EnumGenome.fresh, 1),
                             (EnumGenome.copy, 1),
                             (EnumGenome.crossover, 3),
                             (EnumGenome.mutate, 5))

        BaseGenome.__init__(self, spawn_chances)

    def fresh_genes(self, length):
        """Return a vector of newly randomized values from goodset.

        @param length: The length of the vector.

        @return: The random vector.
        """
        return [random.choice(self.goodset) for _ in range(length)]

    def fresh(self):
        """Construct and return a freshly randomized genome, by
        calling fresh_genes.

        Evolutionary operator.
        """
        child = self.copy()
        child.genes = self.fresh_genes(len(self.genes))
        return child

    def copy(self):
        """Return a copy of self.

        Evolutionary operator.
        """
        return EnumGenome(self.genes, self.goodset, self.spawn_chances)

    def mutate(self):
        """Pick a random gene position and fill it with a random choice
        from the goodset.

        Evolutionary operator.
        """
        child = self.copy()
        i = random.randrange(len(self.genes))
        child.genes[i] = random.choice(self.goodset)
        return child

    def crossover(self):
        """Use genes from both parents to create a new child.

        Evolutionary operator.
        """
        child = self.copy()
        pt1 = random.randrange(len(self.genes))
        pt2 = random.randrange(len(self.genes) - pt1) + pt1
        child.genes[pt1:pt2] = self.partner.genes[pt1:pt2]
        return child
