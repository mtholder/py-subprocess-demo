#!/bin/sh
parent=$(dirname $0)
numleaves=$1
birth=$2
death=$3
"${parent}/generate_true_and_inf_tree.py" "${numleaves}" "${birth}" "${death}" || exit 1
"${parent}/compare_trees.py" simtree inferred.tre > summary.csv || exit 4
