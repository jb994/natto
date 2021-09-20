$MKL_NUM_THREADS =1
$NUMBA_NUM_THREADS =1
$OMP_NUM_THREADS =1
$OPENBLAS_NUM_THREADS =1
import sys
args = sys.argv[1:]
what = args[0]
import matplotlib
matplotlib.use('module://matplotlib-sixel')
import matplotlib.pyplot as plt





debug = False # also set sim_mtx debug manualy ...
directory = 'res3k'
$directory = directory


if what == "run":
    mkdir $directory
    rm $directory/*
    if debug:
        parallel -j 32 --bar --jl job.log ./sim_mtx.py $directory ::: @$(seq 0 13) ::: @$(seq 0 13) ::: @$(seq 0 1)
    else:
        parallel -j 32 --bar --jl job.log ./sim_mtx.py $directory ::: @$(seq 0 56) ::: @$(seq 0 56) ::: @$(seq 0 4)


elif what == "plot":
    import loadblock3
    import numpy as np
    import plot.dendro as dendro
    import natto.input as input
    fdim = 5
    labels = input.get57names()
    if debug:
        res = loadblock3.make_matrix(dim = [14,14,2], fdim = fdim, dir = directory)
        labels = labels[:14]
        unilabels = range(2,5)
    else:
        res = loadblock3.make_matrix(dim = [57,57,5], fdim = fdim, dir = directory)
        unilabels = range(5,14)

    for fd in range(fdim):
        print(f" starting plot: {fd}")
        distancematrix = np.nanmean(res[:,:,:,fd],axis=2)
        plt.imshow(distancematrix); plt.show();plt.close()
        dendro.plot(distancematrix, labels)
        dendro.score(distancematrix,labels,unilabels)

elif what  == '100data':
    '''remove the garbage datasets form the 100'''
    from natto import input
    import basics as ba
    dnames = input.get100names(path='../data')
    #sizes = [ input.load100(dna,path = '../data', subsample=False).X.shape[0] for dna in dnames ]
    sizes = [15776, 17768, 12457, 8307, 7932, 10051, 8041, 8724, 7389, 9285, 10549, 8766, 12334, 2322, 2283, 1898, 3429, 3423, 3840, 5459, 4910, 2674, 2581, 2160, 2292, 2500, 3906, 2914, 3493, 3372, 3940, 3718, 4479, 9685, 7826, 6939, 7145, 62811, 76370, 1425, 64887, 6806, 2881, 2300, 2405, 2186, 25985, 9594, 36952, 49696, 32095, 46272, 48421, 40299, 47923, 43451, 6101, 7789, 11468, 7718, 8069, 7479, 6453, 6950, 8538, 6264, 10979, 14332, 7788, 12974, 2376, 1568, 2683, 2794, 4068, 2768, 2777, 24479, 3007, 31425, 4020, 46046, 5389, 5468, 9339, 4046, 4306, 4791, 15101, 56691, 5299, 4574, 19111, 27713, 11493, 5382, 35086, 60199, 58584, 46546]
    size_cut = [s>5000 for s in sizes]
    sizes = ba.np_bool_select(sizes,size_cut)
    dnames = ba.np_bool_select(dnames,size_cut)
    dnames = [d for d in dnames if not d.startswith('Adipo') and not d.startswith("Colon")]
    print(dnames)
    dnames = [d[:5] for d in dnames]
    from collections import Counter
    print(len(dnames))
    print(Counter(dnames))
    plt.hist(sizes, bins = 25)
    plt.show()



else:
    print("arg should be run or plot")


"""
for i in (seq 0 874)
     for rep in (seq 0 0)
       if ! test -e ./resOMG/(string join _ $i $rep) && echo "$i $rep"; end
end; end |  parallel -j 32 --bar ./combirand_1d.py
#loadblock2 -d 875 11 -f -b 8 resOMG > ~/p3.3.ev
"""






