#!/usr/bin/env python
import sys, os, tempfile
import random
from dendropy import treesim, treesplit, TreeList

def do_sim(birth_rate   , death_rate, num_leaves, rng=None):
    temp_dir = tempfile.mkdtemp()
    model_tree = treesim.birth_death(birth_rate=birth_rate,
                            death_rate=death_rate,
                            ntax=num_leaves,
                            rng=rng)
    ################################################################################
    # Calling seq-gen
    mtf = os.path.join(temp_dir, 'simtree')
    print "temp_dir =", temp_dir
    treefile_obj = open(mtf, 'w')
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
        sg_seed = seed
        
    else:
        if rng is None:
            sg_seed = random.randint(0,100000)
        else:
            sg_seed = rng.randint(0,100000)
    command_line.append('-z%d' % sg_seed)
    command_line.append('simtree')
    
    seq_gen_proc = subprocess.Popen(command_line,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=temp_dir)
    
    dataset = seq_gen_proc.communicate()[0]
    
    
    # seq-gen does not exit with an error code when it fails.  I don't know why!!
    if seq_gen_proc.returncode != 0 or len(dataset) == 0:
        sys.exit('seq-gen failed!\n')
    sd = os.path.join(temp_dir, 'simdata.nex')
    d = open(sd, 'w')
    d.write(dataset)
    # CLOSING THE FILE IS IMPORTANT!  This flushes buffers, assuring that the data
    #  will be written to the filesystem before PAUP is invoked.
    d.close()
    
    ################################################################################
    # PAUP
    pcf = os.path.join(temp_dir, 'execute_paup.nex')
    pc = open(pcf, 'w')
    pc.write('''execute simdata.nex ; 
    hsearch nomultrees ; 
    savetree file=inferred.tre format = NEXUS;
    quit;
    ''')
    pc.close()
    paup_proc = subprocess.Popen(['paup', '-n', pcf], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=temp_dir)
    (o, e) = paup_proc.communicate()
    
    paup_output = os.path.join(temp_dir, 'inferred.tre')
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
    
    os.remove(pcf)
    os.remove(paup_output)
    os.remove(sd)
    os.remove(mtf)
    os.rmdir(temp_dir)
    
    return node_depth_TF_list

def do_rep(rep_num, birth_rate, death_rate, num_leaves, rng=None):
    node_depth_TF_list = do_sim(birth_rate, death_rate, num_leaves, rng=rng)
    summary = open('summary%d.csv' % rep_num, 'w')
    for t in node_depth_TF_list:
        summary.write("%f\t%f\t%d\n" % t)


from Queue import Queue
from threading import Thread
jobq = Queue()
jumpq = Queue()
def worker():
    rng = random.Random()
    if os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED'):
        seed = int(os.environ.get('TREE_INF_TEST_RAND_NUMBER_SEED'))
    else:
        import time
        seed = time.time()
    jump = jumpq.get()
    print "jump = ", jump
    rng.jumpahead(jump*454361)
    while True:
        rep_num = jobq.get()
        sys.stderr.write("%d started\n" % rep_num)
        try:
            do_rep(rep_num, birth_rate, death_rate, num_leaves, rng)
        except:
            from cStringIO import StringIO
            import traceback
            err = StringIO()
            traceback.print_exc(file=err)
            sys.stderr.write("Worker dying.  Error in job.start = %s" % err.getvalue())
            sys.exit(1)
        jobq.task_done()
    return

# We'll keep a list of Worker threads that are running in case any of our code triggers multiple calls
_WORKER_THREADS = []

def start_worker(num_workers):
    """Spawns worker threads such that at least `num_workers` threads will be
    launched for processing jobs in the jobq.

    The only way that you can get more than `num_workers` threads is if you
    have previously called the function with a number > `num_workers`.
    (worker threads are never killed).
    """
    assert num_workers > 0, "A positive number must be passed as the number of worker threads"
    
    num_currently_running = len(_WORKER_THREADS)
    for i in range(num_currently_running, num_workers):
        jumpq.put(i)
    for i in range(num_currently_running, num_workers):
        sys.stderr.write("Launching Worker thread #%d\n" % i)
        t = Thread(target=worker)
        _WORKER_THREADS.append(t)
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    num_leaves = int(sys.argv[1])
    assert num_leaves > 2
    birth_rate = float(sys.argv[2])
    assert birth_rate > 0.0
    death_rate = float(sys.argv[3])
    assert birth_rate >= 0.0
    num_reps = int(sys.argv[4])
    assert num_reps > 0
    
    for i in range(num_reps):
        jobq.put(i)
    # this launches 4 worker threads. Each of these will call the function `worker`
    start_worker(4)
    
    # this causes the process to wait until the queue is done
    jobq.join() 
