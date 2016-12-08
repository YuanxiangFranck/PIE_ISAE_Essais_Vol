import numpy as np

def NearestNeighbor(x, k, l, binary=False):
    """
    Return the l worst point of x considering the mean of the distances between the k nearest neighbors.
    l : int
    x : list of points
    k : int
    binary : boolean
    """

    inf = 1e20
    n = len(x)
    res = False
    stockDist = np.asarray([inf]*n)
    if k>n or l>n:
        Print("It is not possible to find the l biggest with the neighbors method with x smaller than l")
    else :
        for i in range(n):
            distance = [inf]*n
            for j in range(0, n):
                if i != j and not binary :
                    distance[j] = np.linalg.norm(x[i]-x[j])
            distance.sort()
            stockDist[i] = np.mean(distance[0:k-1])
        res = lBigger(stockDist,l)
    return res

def lBigger(x, l):
    """
    Return the indice of the l higher values in x
    """
    res = False
    if l > len(x):
        print("It is not possible to find the l biggest values in a list of less than l values")
    else :
        valRes = x[0:l]
        res = np.arange(l)
        for i in range(l,len(x)):
            low = lower(valRes)
            if x[i] > valRes[low]:
                res[low]=i
                valRes[low]=x[i]
    return res

def lower(x):
    """
    Return the indice of the lower value in x
    """
    ind = np.argmin(x)
    return ind

if __name__ == "__main__":
    X = np.asarray([[1,1000],[2,1],[3,0],[20,1],[2,-1],[0,-4],[8,10],[15,10]])
    print(X)
    NN = NearestNeighbor(X,3,4);
    print(NN)
