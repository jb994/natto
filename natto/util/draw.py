from itertools import permutations
import random
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from umap import UMAP
import seaborn as sns

from matplotlib_venn import *

def umap(X,Y, reducer = None,
        title="No title",
        acc : "y:str_description"={}, 
        black = None, 
        show=True,
        markerscale=4,
        size=None):
    assert reducer != None  , "give me a reducer"
    plt.title(title, size=20)
    
    
    
    # make a list of colors 
    colors = list(permutations([0,.25,.5,.75,1],3))
    random.seed(5) #making shuffle consistent
    random.shuffle(colors)
    f = lambda cm: [cm.colors[i] for i in range(len(cm.colors))]
    #colors = f(plt.cm.get_cmap('tab20b')) +f(plt.cm.get_cmap('tab20c')) 
    colors = f(plt.cm.get_cmap('tab20'))
    colors += f(plt.cm.get_cmap("tab20b"))
    colors += f(plt.cm.get_cmap("tab20c"))
    # put the list in col for usage
    col = { i-2:e for i,e in enumerate(colors)}
    col.update( {a+100:b for a,b in col.items()}  )



    Y=np.array(Y)
    
    
    size=  max( int(4000/Y.shape[0]), 1) if not size else size
    
    if type(black) != type(None): 
        embed = reducer.transform(black)
        plt.scatter(embed[:, 0], embed[:, 1],c=[(0,0,0) for e in range(black.shape[0])], 
                    s=size,
                    label='del')
    
    embed = reducer.transform(X)
    for cla in np.unique(Y):
        plt.scatter(embed[Y==cla, 0], embed[Y==cla, 1],
                    color=col[cla],
                    s=size,
                    label= acc.get(cla,str(cla)))
    #plt.axis('off')
    plt.xlabel('UMAP 2')
    plt.ylabel('UMAP 1')


    plt.legend(markerscale=markerscale,ncol=5,bbox_to_anchor=(1, -.12) )
    if show: plt.show()
    return reducer

def cmp2(Y1,Y2,X1,X2,title=('1','2'),red=None, save=None):    

    sns.set(font_scale=1.2,style='white')
    if not red:
        red = UMAP()
        red.fit(np.vstack((X1,X2)))
    plt.figure(figsize=(16,8))    

    #plt.tight_layout()    
    ax=plt.subplot(121)
    umap(X1,Y1,red,show=False,title=title[0],size=4,markerscale=4)
    ax=plt.subplot(122)
    umap(X2,Y2,red,show=False,title=title[1],size=4,markerscale=4)
    if save:
        plt.tight_layout()
        plt.savefig(save, dpi=300)
    plt.show()


def cmp3(Y1,Y2,X1,X2,title=('1','2'),red=None, save=None):    

    sns.set(font_scale=1.2,style='white')
    if not red:
        red = UMAP()
        red.fit(np.vstack((X1,X2)))
    plt.figure(figsize=(24,8))    

    #plt.tight_layout()    
    ax=plt.subplot(131)
    umap(X1,Y1,red,show=False,title=title[0],size=4,markerscale=4)
    ax=plt.subplot(132)
    umap(X2,Y2,red,show=False,title=title[1],size=4,markerscale=4)
    ax=plt.subplot(133)
    umap(np.vstack((X1,X2)),
            [1]*len(Y1)+[2]*len(Y2),
            red,
            show=False,
            title="Combined",
            size=4,
            markerscale=4, acc={1:title[0] , 2:title[1]})
    if save:
        plt.tight_layout()
        plt.savefig(save,dpi=300)
    plt.show()

def venn(one,two: 'boolean array', labels :"string tupple"):
    selover = [a and b for a,b in zip (one,two)]
    comb = sum(selover)
    v = venn2(subsets = {'10': sum(one)-comb, '01': sum(two)-comb, '11': comb}, set_labels = labels)
    plt.show()



def simpleheatmap(canvas):
        df = DataFrame(canvas)
        sns.heatmap(df, annot=True)
        
        #df = DataFrame(canvas[:y1map.len,:y2map.len])
        #s= lambda y,x: [ y.getitem[k] for k in x]
        #sns.heatmap(df,annot=True,yticklabels=y1map.itemlist,xticklabels=y2map.itemlist, square=True)
        plt.show()

def doubleheatmap(canvas, cleaned, y1map, y2map, rows, cols, save=None):    

    sns.set(font_scale=1.2,style='white')
    plt.figure(figsize=(12,5))    

    #plt.tight_layout()    
    ax=plt.subplot(121)
    plt.title('Normalized Matches',size=20)
    heatmap(canvas,y1map,y2map,rows,cols, show=False)
    ax=plt.subplot(122)
    plt.title('Processed Matrix',size=20)
    heatmap(cleaned,y1map,y2map,rows,cols, show=False)
    if save:
        plt.tight_layout()
        plt.savefig(save, dpi=300)
    plt.show()

def heatmap(canvas,y1map,y2map,row_ind,col_ind, show=True):
        # there is a version that sorts the hits to the diagonal in util/bad... 
        paper = True
        
        sorting = sorted(zip(col_ind, row_ind))
        col_ind, row_ind= list(zip(*sorting))
        
        # some rows are unused by the matching,but we still want to show them:
        order= list(row_ind) + list(set(y1map.integerlist)-set(row_ind) )
        canvas = canvas[order]

        xlabels = y2map.itemlist 
        ylabels = [y1map.getitem[r]for r in order]

        df = DataFrame(-canvas)

        if paper:
            sns.heatmap(df,xticklabels=xlabels,yticklabels=ylabels, annot=False ,linewidths=.5,cmap="YlGnBu" )
            plt.xlabel('Clusters data set 2')
            plt.ylabel('Clusters data set 1')
        else:
            sns.heatmap(df,xticklabels=ylabels,yticklabels=xlabels, annot=True)
        #df = DataFrame(canvas[:y1map.len,:y2map.len])
        #s= lambda y,x: [ y.getitem[k] for k in x]
        #sns.heatmap(df,annot=True,yticklabels=y1map.itemlist,xticklabels=y2map.itemlist, square=True)
        if show:
            plt.show()
