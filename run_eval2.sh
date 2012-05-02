#!/bin/sh
parent=$(dirname $0)
numleaves=$1
birth=$2
death=$3
"${parent}/generate_data.py" "${numleaves}" "${birth}" "${death}" > simtree || exit 1
paup -n "${parent}/execute.nex" || exit 3
"${parent}/compare_trees.py" simtree inferred.tre > summary.csv || exit 4
