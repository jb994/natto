import numpy as np
import scanpy as sc
import matplotlib.pyplot as plt
from lmz import *
import sklearn

####
# ft select
###
def transform( means, var,plot, stepsize=.5, ran=3, minbin=0 ):
    x = np.arange(minbin * stepsize, ran, stepsize) #-> .5,1,1.5,2,2.5 ...

    #items = [(m, v) for m, v in zip(means, var)] #-> items = list(zip(means,var))
    items = Zip(means,var)

    boxes = [[i[1] for i in items if r < i[0] < r + (stepsize)] for r in x]
    y = np.array([np.median(st) for st in boxes])
    y_std = np.array([np.std(st) for st in boxes])
    x = x + (stepsize / 2)
    # draw regression points
    if plot:
        plt.scatter(x, y, label='Mean of bins', color='k')

    nonan = np.isfinite(y)
    x = x[nonan]
    y = y[nonan]
    y_std = y_std[nonan]
    x = x.reshape(-1, 1)
    return x, y, y_std


def get_expected_values(x, y, x_all):
    mod = sklearn.linear_model.HuberRegressor()
    mod.fit(x, y)
    res = mod.predict(x_all.reshape(-1, 1))
    firstbin = y[0]
    firstbin_esti = mod.predict([x[0]])
    res[x_all < x[0]] = max(firstbin, firstbin_esti)
    return res


def getgenes_natto(adata, selectgenes, title,
        mean=(.015,4),
        bins=(.25,1),
        plot=True):

    matrix= adata.to_df().to_numpy()
    
    a = np.expm1(matrix)
    var = np.var(a, axis=0)
    meanex = np.mean(a, axis=0)

    print("disp= var/mean might produce a warning but we will catch that later")
    disp = var / meanex

    Y = np.log(disp)
    X = np.log1p(meanex)


    #plt.scatter(X,Y)
    #plt.show()

    mask = np.array([not np.isnan(y) and me > mean[0] and me < mean[1] for y, me in zip(disp, X)])

    if plot:
        plt.figure(figsize=(11, 4))
        plt.suptitle(f"gene selection: {title}", size=20, y=1.07)
        ax = plt.subplot(121)
        plt.scatter(X[mask], Y[mask], alpha=.2, s=3, label='all genes')
    


    x_bin, y_bin, ystd_bin = transform(X[mask].reshape(-1, 1),
                                            Y[mask],plot,
                                            stepsize=bins[0],
                                            ran=mean[1],
                                            minbin=bins[1] )


    
    y_predicted = get_expected_values(x_bin, y_bin, X[mask])
    std_predicted = get_expected_values(x_bin, ystd_bin, X[mask])
    Y[mask] -= y_predicted
    Y[mask] /= std_predicted

    srt = np.argsort(Y[mask])
    accept = np.full(Y[mask].shape, False)
    accept[srt[-selectgenes:]] = True

    if plot:
        srt = np.argsort(X[mask])
        plt.plot(X[mask][srt], y_predicted[srt], color='k', label='regression')
        plt.plot(X[mask][srt], std_predicted[srt], color='g', label='regression of std')
        plt.scatter(x_bin, ystd_bin, alpha=.4, label='Std of bins', color='g')
        plt.legend(bbox_to_anchor=(.6, -.2))
        plt.title("dispersion of genes")
        plt.xlabel('log mean expression')
        plt.ylabel('dispursion')
        ax = plt.subplot(122)
        plt.scatter(X[mask], Y[mask], alpha=.2, s=3, label='all genes')
        g = X[mask]
        d = Y[mask]
        plt.scatter(g[accept], d[accept], alpha=.3, s=3, color='r', label='selected genes')
        plt.legend(bbox_to_anchor=(.6, -.2))
        plt.title("normalized dispersion of genes")
        plt.xlabel('log mean expression')
        plt.ylabel('dispursion')
        plt.show()

        print(f"ft selected:{sum(accept)}")


    
    raw = np.zeros(len(mask))
    raw[mask] = Y[mask] 


    mask[mask] = np.array(accept)
    return mask, raw


##################
# MAKE EVEN AND BASIC_FILTERING
###################
def basic_filter(data, min_counts=3, min_genes=200):
    # filter cells
    [sc.pp.filter_cells(d, min_genes=min_genes, inplace=True) for d in data]

    # filter genes
    genef = [sc.pp.filter_genes(d, min_counts=min_counts, inplace=False)[0] for d in data]
    geneab = np.any(np.array(genef), axis=0)
    for i, d in enumerate(data):
        data[i] = d[:, geneab]
    return data

def make_even(data):
        # assert all equal
        size = data[0].X.shape[1]
        assert all([size == other.X.shape[1] for other in data])

        # find smallest
        counts = [e.X.shape[0] for e in data]
        smallest = min(counts)

        for a in data:
            if a.X.shape[0] > smallest:
                sc.pp.subsample(a,
                                fraction=None,
                                n_obs=smallest,
                                random_state=0,
                                copy=False)
        return data

def normlog(data):
    [sc.pp.normalize_total(d, 1e4) for d  in data]
    [sc.pp.log1p(d) for d in data]
    return data


def unioncut(gene_lists, data):
    genes = np.any(np.array(gene_lists), axis=0)
    return [d[:, genes].copy() for d in data]
