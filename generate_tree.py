#!/usr/bin/env python
import sys, os
import random
from dendropy import treesim
num_leaves = int(sys.argv[1])
assert num_leaves > 2
birth_rate = float(sys.argv[2])
assert birth_rate > 0.0
death_rate = float(sys.argv[3])
assert birth_rate >= 0.0
rng = random.Random()
if os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED'):
    rng.seed(int(os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED')))

t = treesim.birth_death(birth_rate=birth_rate,
                        death_rate=death_rate,
                        ntax=num_leaves,
                        rng=rng)
sys.stdout.write("%s;\n" % str(t))
