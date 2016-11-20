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
		print("You cannot take the K lower values in X if K is higher than the number of values in X")
	else :
		sort = sorted(x)
		res = [0]*k
		for i in range(0,k):
			res[i]=sort[i]
			
	return res
	
	
	