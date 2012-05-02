#!/usr/bin/env python
import sys, os
import random
from dendropy import treesim, treesplit, TreeList
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

model_tree = treesim.birth_death(birth_rate=birth_rate,
                        death_rate=death_rate,
                        ntax=num_leaves,
                        rng=rng)
################################################################################
# Calling seq-gen
treefile_obj = open('simtree', 'w')
treefile_obj.write("%s;\n" % str(model_tree))
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
# CLOSING THE FILE IS IMPORTANT!  This flushes buffers, assuring that the data
#  will be written to the filesystem before PAUP is invoked.
d.close()

################################################################################
# PAUP
pcf = 'execute_paup.nex'
pc = open(pcf, 'w')
pc.write('''execute simdata.nex ; 
hsearch nomultrees ; 
savetree file=inferred.tre format = NEXUS;
quit;
''')
pc.close()
paup_proc = subprocess.Popen(['paup', '-n', pcf], 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
(o, e) = paup_proc.communicate()

paup_output = 'inferred.tre'
# seq-gen does not exit with an error code when it fails.  I don't know why!!
if paup_proc.returncode != 0 or not os.path.exists(paup_output):
    sys.exit(e)


# read true tree with the inferred tree (because it is nexus)
inf_tree_list = TreeList.get_from_path(paup_output, 
                                                "NEXUS",
                                                taxon_set=model_tree.taxon_set)
assert len(inf_tree_list) == 1
inferred_tree = inf_tree_list[0]

# determine which splits were missed
treesplit.encode_splits(inferred_tree)
treesplit.encode_splits(model_tree)
missing = model_tree.find_missing_splits(inferred_tree)
# sort the nodes of the true tree by depth and ask whether or not they were recovered
node_depth_TF_list = []
for node in model_tree.postorder_node_iter():
    children = node.child_nodes()
    if children and node.parent_node:
        first_child = children[0]
        node.depth = first_child.depth + first_child.edge.length
        if node.edge.split_bitmask in missing:
            recovered = 0
        else:
            recovered = 1
        node_depth_TF_list.append((node.depth, node.edge.length, recovered))
    else:
        node.depth = 0.0

node_depth_TF_list.sort()

summary = open('summary.csv', 'w')
for t in node_depth_TF_list:
    summary.write("%f\t%f\t%d\n" % t)
