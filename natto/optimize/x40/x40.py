from lmz import Map,Zip,Filter,Grouper,Range,Transpose
from natto.optimize import util  as d
from natto import input
import numpy as np
from functools import partial
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from natto.process import Data
from natto.optimize.plot.dendro import drawclustermap
from natto import process
from ubergauss import tools
import random
from sklearn.metrics import adjusted_rand_score, f1_score
from sklearn.cluster import SpectralClustering,KMeans, AgglomerativeClustering


def preprocess( repeats =7, ncells = 1500):
    datasets = input.get40names()
    random.seed(43)
    loaders =  [ partial( input.load100,
                          data,
                          path = "/home/ubuntu/repos/natto/natto/data",
                          subsample=ncells)
                 for data in datasets]

    it = [ [loaders[i],loaders[j]] for i in Range(datasets) for j in range(i+1, len(datasets))]
    def f(loadme):
        a,b = loadme
        print('#'*80)
        print('#'*80)
        print(a,b)
        return [Data().fit([a(),b()],
            visual_ftsel=False,
            pca = 0,
            make_readcounts_even=True,
            umaps=[],
            sortfield = -1,
            make_even=True) for i in range(repeats)]
    res =  tools.xmap(f,it,32)
    tools.dumpfile(res,'data.dmp')

def calc_mp20(meth,out = 'calc.dmp', infile='data.dmp', shape=(40, 40, 5)):
    # label is the name that we give to the plot.
    # meth is a function that takes a Data object and calculates a similarity

    m = np.zeros(shape, dtype=float)
    data = tools.loadfile(infile)
    data.reverse() # because we use pop later
    it = []

    # so we generate the data to be executed [i,j,repeatid,data]
    for a in range(m.shape[0]):
        for b in range(m.shape[1]):
            if b > a:
                for r, dat in enumerate(data.pop()):
                    it.append((a, b, r, dat))

    # execute
    def f(i):
        b, a, c, data = i
        return b, a, c, meth(data)

    for a, b, c, res in tools.xmap(f, it, 32):
        m[b, a, c] = np.median(res)
        m[a, b, c] = m[b, a, c]

    #res = np.median(m, axis=2)
    tools.dumpfile(m, out)


if __name__ == "__main__":
    preprocess(5,2000)
    jug = Range(50, 1400, 50)
    for numgenes in jug:
        calc_mp20(partial(d.jaccard, ngenes=numgenes),out=f"jacc/{numgenes}.dmp")
        calc_mp20(partial(d.cosine, ngenes=numgenes),out=f"cosi/{numgenes}.dmp")
