This repository is for a demonstration of using python to invoke other 
    processes.

If we want to repeat a multi-step, multi-executable pipeline, a shell script 
    is often the best choice.
    
Executing:
###################################################
$ sh master.sh 10 1 .2 5
###################################################
Will create 5 simulation replicates. In each replicate (see run_eval.sh):
    1. a birth-death tree (speciation rate = 1, extinction rate=0.2) with 10 
        leaves will be simulated (using generate_tree.py)
    2. 1000 sites of DNA sequences will be simulated (using seq-gen and -mHKY as
        the model
    3. an approximation of the most-parsimonious tree will be found (using PAUP)
    4. we summarize (in a tab-delimited file "summary.csv") the depth of 
        different nodes in the model tree, the branch length subtending the 
        node, and a 1 (success) or 0 (failure) indication of whether the branch 
        was recovered.
        
Note:
    * This approach creates lots of files, but this makes each step
        very transparent
    * the steps using random numbers respond to the existence of a variable
        called TREE_INF_TEST_RAND_NUMBER_SEED in the environment.  Setting a
        seed for random number generators is important when you need to debug
        scripts that rely on random numbers.  Putting this dependence using 
        environmental variables, lets you drop into or out of debugging mode
        without modifying your code.
    * Using the filesystem as the means of communicating between processes is 
        pretty robust.  But :
            * it is not thread-safe (running independent instances
                in the same directory can lead to clashes), 
            * you can run into issues with random number generators that use the
                wall-clock time in seconds (as opposed to a finer-scale
                gradation of time) causing different processes to use the same 
                random number seeds, and
            * it is not efficient (parsing overhead, and simply the slow speed 
                of accessing the filesystem)
