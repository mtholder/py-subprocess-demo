#!/bin/sh
parent=$(dirname $0)
numleaves=$1
birth=$2
death=$3
"${parent}/do_sim_and_eval.py" "${numleaves}" "${birth}" "${death}" || exit 1
