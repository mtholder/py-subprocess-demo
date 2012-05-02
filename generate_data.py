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
    seed = int(os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED'))
else:
    import time
    seed = time.time()

rng.seed(seed)

t = treesim.birth_death(birth_rate=birth_rate,
                        death_rate=death_rate,
                        ntax=num_leaves,
                        rng=rng)

treefile_obj = open('simtree', 'w')
treefile_obj.write("%s;\n" % str(t))
# CLOSING THE FILE IS IMPORTANT!  This flushes buffers, assuring that the data
#  will be written to the filesystem before seq-gen is invoked.
treefile_obj.close() 


import subprocess
command_line = ['seq-gen',
                '-mHKY',
                '-on',
            ]
if os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED'):
    command_line.append('-z%d' % seed)
command_line.append('simtree')

seq_gen_proc = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

dataset = seq_gen_proc.communicate()[0]


# seq-gen does not exit with an error code when it fails.  I don't know why!!
if seq_gen_proc.returncode != 0 or len(dataset) == 0:
    sys.exit('seq-gen failed!\n')

d = open('simdata.nex', 'w')
d.write(dataset)
