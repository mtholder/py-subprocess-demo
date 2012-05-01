#!/bin/sh
parent=$(dirname $0)
numleaves=$1
birth=$2
death=$3
"${parent}/generate_tree.py" "${numleaves}" "${birth}" "${death}" > simtree || exit 1
if test -z "${TREE_INF_TEST_RAND_NUMBER_SEED}"
then
    export TREE_INF_TEST_RAND_NUMBER_SEED="${RANDOM}"
fi

seq-gen -mHKY "-z${TREE_INF_TEST_RAND_NUMBER_SEED}" -on simtree > simdata.nex || exit 2
paup -n "${parent}/execute.nex" || exit 3
"${parent}/compare_trees.py" simtree inferred.tre > summary.csv || exit 4
