#!/bin/sh
nreps=$4
pref="n${1}b${2}d${3}"
mkdir "n${1}b${2}d${3}" || exit
for ((i=0; i<$nreps; ++i))
do
    dn="${pref}/rep${i}"
    mkdir $dn || exit 1
    cd $dn || exit 1
    ../../run_eval3.sh "${1}" "${2}" "${3}"
    cd -
done
