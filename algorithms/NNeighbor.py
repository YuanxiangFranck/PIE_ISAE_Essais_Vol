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
	stockDist = [inf]*n
	for i in range(0,n): 
		distance = [inf]*n
		for j in range(0,n):
			if i != j and !binary :
				distance[j] = np.linalg.norm(x[i]-x[j])
		low = distance.sort()[0:k-1]
		stockDist[i] = np.mean(low)
	
def lBigger(x,l):
	"""
	Return the indice of the l higher values in x
	"""
	res = False
	if l > len(x):
		print("It is not possible to find the l biggest values in a list of less than l values")
	else : 
		valRes = x[0:l]
		res = range(0,l)
		for i in range(l,len(x)):
			low = lower(valRes)
			if x(i) > valRes[low]:
				res[low]=i
				valRes[low]=x[i]
	return res
	
def lower(x):
	"""
	Return the indice of the lower value in x
	"""
	mini = min(x)
	ind = x.find(mini)
	return ind