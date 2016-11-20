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
	sort = [[]]*l
	for i in range(0,len): 
		distance = [inf]*n
		for j in range(0,len):
			if i != j and !binary :
				distance[j] = np.linalg.norm(x[i]-x[j])
				

				
				
	
def KLower (k,x) : 
	"""
	Return the indice of the k lower values in x
	k : the number of indices to obtain
	x : values to order
	"""
	
	res = False
	taille = len(x)
	
	if k > taille :
		print("You cannot take the k lower values in x if k is higher than the number of values in x")
	else :
		indRes = range(0,k)
		valRes = x[0:k-1]
		for i in range(k,taille):
		big = bigger(valRes)
			ind = indRes[big]
			if x(i) < x(ind]):
				indRes[big]=i
				valRes[ind]=x(i)
	return indRes
	
def bigger (x):
	"""
	The list of values whereyou want to find the bigger value
	"""
	maxi = max(x)
	ind = x.find(maxi)
	return ind
	