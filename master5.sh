#!/bin/sh
nreps="${4}"
pref="n${1}b${2}d${3}"
mkdir "n${1}b${2}d${3}" || exit
cd "${pref}" || exit 1
../do_multi_sim_and_eval.py "${1}" "${2}" "${3}" "${nreps}"
cd -
