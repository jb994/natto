import basics as ba 
from natto.input import load 
from natto.optimize import noise  as n 
import numpy as np 
from functools import partial
import natto.process as p 
from basics.sgexec import sgeexecuter as sge

def process(level, c):
    l =np.array(level)
    return l.mean(axis = 0 )[c]

def processVar(level, c):
    l =np.array(level)
    return l.var(axis = 0 )[c]

def processstd(level, c):
    l =np.array(level)
    return l.std(axis = 0 )[c]

cluster = partial(p.leiden_2,resolution=.5)

cluster = partial(p.gmm_2, cov='full', nc = 8)

l_3k = partial(load.load3k, subsample=1500)
l_6k = partial(load.load6k, subsample=1500)
#l_stim = partial (load.loadpbmc,path='../data/immune_stim/9',subsample=1500,seed=None)
l_p7e = partial(load.loadpbmc, path='../data/p7e',subsample=1500,seed=None)
l_p7d = partial(load.loadpbmc, path='../data/p7d',subsample=1500,seed=None)
l_h1 = partial(load.loadgruen_single, path = '../data/punk/human1',  subsample=1500)
l_h3 = partial(load.loadgruen_single, path = '../data/punk/human3',  subsample=1500)

def run(loader, rname):
    s=sge()
    for level in range(0,110,10):
        s.add_job( n.get_noise_run_moar , [(loader, cluster, level) for r in range(50)] )
    rr= s.execute()

    res= [process(level, 0) for level in rr]
    std=[processstd(level, 0) for level in rr]
    print(f"a={res}\nb={std}\n{rname}=[a,b,'RARI']")


myloaders=[l_3k, l_6k, l_h1,l_h3,l_p7e, l_p7d]
lnames = ['3k','6k','h1','h3','p7e','p7d']
for loader,lname in zip(myloaders, lnames):
    run(loader, f'{lname}_g8')
