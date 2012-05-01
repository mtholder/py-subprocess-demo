#!/usr/bin/env python
import sys, os
import dendropy
true_treefile = sys.argv[1]
os.path.exists(true_treefile)
inferred_treefile = sys.argv[2]
os.path.exists(inferred_treefile)

# read true tree with the inferred tree (because it is nexus)
data_set =  dendropy.DataSet.get_from_path(inferred_treefile,
                                           "NEXUS")
assert len(data_set.taxon_sets) == 1
taxa = data_set.taxon_sets[0]
assert len(data_set.tree_lists) == 1
assert len(data_set.tree_lists[0]) == 1
inferred_tree = data_set.tree_lists[0][0]

# read true tree with the same taxa
true_tree_list = dendropy.TreeList.get_from_path(true_treefile, 
                                                 "NEWICK",
                                                 taxon_set=taxa)
assert len(true_tree_list) == 1
true_tree = true_tree_list[0]

# determine which splits were missed
dendropy.treesplit.encode_splits(inferred_tree)
dendropy.treesplit.encode_splits(true_tree)
missing = true_tree.find_missing_splits(inferred_tree)
# sort the nodes of the true tree by depth and ask whether or not they were recovered
node_depth_TF_list = []
for node in true_tree.postorder_node_iter():
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
        
for t in node_depth_TF_list:
    sys.stdout.write("%f\t%f\t%d\n" % t)
