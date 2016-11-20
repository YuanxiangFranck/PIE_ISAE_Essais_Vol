import numpy as np 

def NearestNeighbor (x,k,l,binary=False):
	"""
	Return the l worst point of x considering the mean of the distances between the k nearest neighbors. 
	l : int 
	x : list of points
	k : int
	binary : boolean 
	"""
	
	inf = 1e20;
	n = len(x)
	res = range(0,l) 
	stockDist = []*n
	for i in range(0,n): 
		distance = [inf]*n
		for j in range(0,n):
			if i != j and !binary :
				distance[j] = np.linalg.norm(x[i]-x[j])
		low = distance.sort()[0:k-1]
		stockDist[i] = np.mean(low)
	