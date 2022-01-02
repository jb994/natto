
from lmz import *
from sklearn.mixture import _gaussian_mixture as _gm
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances as ed
from sklearn.mixture import GaussianMixture as gmm 


#############
# KMEANS 
############
def assign(x1,x2,c1,c2):
    r = ed(x1,c1)
    r2 = ed(x2,c2)
    r3=np.concatenate((r,r2), axis=1) #euclidean distances of points
    z = np.argmin(r3, axis = 1) # cluster with minimal euclidean distance
    res = np.array( [zz if zz < c1.shape[0] else zz-c1.shape[0]  for zz in z] ) # y


    return res,  np.argmin(r, axis = 1) !=  np.argmin(r2, axis = 1) 


def centers(y,X):
    cents = []
    for i in np.unique(y):
        cents.append(X[y==i].mean(axis=0))
    return np.array(cents)


def optimize_kmeans(X1,X2,y): 
    c1, c2 = centers(y,X1), centers(y,X2)
    #c2 = h.hungsort(c1,c2)
    y,e = assign(X1,X2,c1,c2)
    return y,e


#######
# Multi input KMEANS
#######
def multi_assign(X, c):
    listOfRs = []
    r_n = ed(X[0], c[0])

    listOfEDs = [np.argmin(r_n, axis=1)]
    for i in range(1,len(X)):
        r_i = ed(X[i],c[i])
        r_n = np.concatenate((r_n, r_i), axis=1)
        listOfEDs.append(np.argmin(r_i, axis=1)) # Used to find error

    clustersByX = np.stack(listOfEDs, axis=0)

    z = np.argmin(r_n, axis=1)
    res = np.array( [zz if zz < c[0].shape[0] else zz-(zz//c[0].shape[0])*c[0].shape[0]  for zz in z] )

    e = np.all(clustersByX == clustersByX[0,:], axis=0)
#    e = np.argmin(ed(X[0],c[0]), axis = 1) !=  np.argmin(ed(X[1], c[1]), axis = 1) 

    return res, e


def optimize_multi_kmeans(XList, y):
    cList = []
    for x in XList:
        cList.append(centers(y, x))
    y,e = multi_assign(XList, cList)
    return y,e




###################
#  OPTIMIZE GMM FOR 2 DATA SETS 
##################

def hot1(y): 
    # be sure to start with label 0 ... 
    uy =  y.max()+1
    r= np.zeros((len(y), uy)) 
    r[range(len(y)), y] =1 
    return r 


def get_means_resp(X,log_resp, cov):
    _, means_, covariances_ = _gm._estimate_gaussian_parameters(X, np.exp(log_resp), 1e-6, cov)
    precisions_cholesky_    = _gm._compute_precision_cholesky( covariances_, cov)
    log_resp                = _gm._estimate_log_gaussian_prob( X, means_, precisions_cholesky_,cov)
    return means_, log_resp


def optimize(X1,X2,y, cov='tied'): 
    log_resp = hot1(y)  # init 
    m1, l1 = get_means_resp(X1,log_resp,cov)
    m2, l2 = get_means_resp(X2,log_resp,cov)
    #(a,b),_ = h.hungarian(m1,m2) 
    #assert np.all(np.diff(b) > 0)
    log_resp = l1+l2
    return log_resp.argmax(axis=1), l1.argmax(axis=1)!=l2.argmax(axis=1), (l1.argmax(axis=1),l2.argmax(axis=1))



###################
#  OPTIMIZE GMM FOR MANY DATA SETS 
##################


def optimize_MANY(XXX,y, cov='tied'): 
    log_resp = hot1(y)  # init 
    mmm, lll =  Transpose([get_means_resp(x,log_resp,cov) for x in XXX])
    #log_resp = l1+l2 
    # l contains for each cluster( horizontal ) a probability for each cell( vertical )
    log_resp = np.array(lll).sum(axis=0)

    all_the_labels = [ l.argmax(axis=1)  for l in lll]
    all_the_probas = [ l.max(axis=1)  for l in lll]
    erer = [ np.logical_not(np.all( np.array(a) == a[0]  ))   for a in zip(*all_the_labels)] # are all entries the same?
    return log_resp.argmax(axis=1),erer, all_the_labels, lll

def multitunnelclust(XXX,y, method = 'full', n_iter=100, debug = False):
    for asd in range(n_iter):
        yold = y.copy()
        y , e, all_labels, all_probas =  optimize_MANY(XXX,y,cov=method)
        chang = sum(y!=yold)
        if debug > 1: 
            print(f"changes in iter:  {chang}")
        if chang == 0:
            if debug:print(f"model converged after {asd} steps")
            break
    else:
        assert False, "did not converge"
    return y,e, all_labels, all_probas







##################3
#  MAIN FUNCTION IS HERE;; SIMUCLUST 
######################

def init(X,clusts=10, cov = 'tied'):
    return gmm(n_components=clusts, n_init=30, covariance_type=cov).fit_predict(X) 


def optistep(X1,X2,y,method):
    if method == 'kmeans':
        return optimize_kmeans(X1,X2,y)
    else:
        return optimize(X1,X2,y, cov=method)

def simulclust(X1,X2,y, method = 'full', n_iter=100, debug = False):
    for asd in range(n_iter):
        yold = y.copy()
        y , e, s1s2=  optistep(X1,X2,y,method) 
        chang = sum(y!=yold)
        if debug > 1: 
            print(f"changes in iter:  {chang}")
        if chang == 0:
            if debug:print(f"model converged after {asd} steps")
            break
    else:
        assert False, "did not converge"
    return y,e, s1s2

def tunnelclust(X1,X2, method = 'full', n_iter=100, debug = False):
    y = init(X1, clusts = 25) 
    return simulclust(X1,X2,y,method=method, n_iter=n_iter, debug=debug)[2]

    




'''
so we want to use as much as possible from sklearn.. so we read the code..: 

we assume init is given.. 

reg_covar:  float, defaults to 1e-6.

base mixture: 

    fit_predict: 
            # EXPECT
            log_prob_norm, log_resp = self._estimate_log_prob_resp(X)
            #log_prob_norm =  np.mean(log_prob_norm)
            
            # MAXIMIZE 
            self._m_step(X, log_resp)

            return log_resp.argmax(axis=1)

    gauss mix: 

        def _estimate_log_prob(self, X):
                return _estimate_log_gaussian_prob(
                            X, self.means_, self.precisions_cholesky_, self.covariance_type)

        def _m_step(self, X, log_resp):
            """M step.
            Parameters
            ----------
            X : array-like, shape (n_samples, n_features)
            log_resp : array-like, shape (n_samples, n_components)
                Logarithm of the posterior probabilities (or responsibilities) of
                the point of each sample in X.
            """
            n_samples, _ = X.shape
            self.weights_, self.means_, self.covariances_ = (
                _estimate_gaussian_parameters(X, np.exp(log_resp), self.reg_covar,
                                              self.covariance_type))
            self.weights_ /= n_samples
            self.precisions_cholesky_ = _compute_precision_cholesky(
                self.covariances_, self.covariance_type)
'''



