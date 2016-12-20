# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 15:51:39 2016

@author: Matthieu
"""

import numpy as np

def SymmetryTest(signal1, signal2, error):
    """
    
    
    Inputs : 
    
    - signal1, signal2 : two signals of the class SignalData to compare 
    (generally signal1 -> "...CHA", and signal2 -> "...CHB"  )
    
    - error : the result will be False if there is at least one value which is 
    out of the relative error box 
    (error is a percentage, example : error = 0.01 for 1 percent) 
    
    Output :
    
    Result : an array, wich first value is boolean, indicates if the two imput 
    signals are the same (according to the accepted error)
    the next values are the index of the signal.data where the differences where found
    """
    
    result =[True]
    error = abs(error)
    index = []
    sig1 = signal1.data
    sig2 = signal2.data   
    
    for i,s in enumerate(sig1):
        sig2 = signal2.data
        if (s != 0):
            if abs((s-sig2[i])/s) > error :
                result = [False]
                index.append(i)
        else:
            if abs(sig2[i]) > error :
                result = [False]
                index.append(i)
                
    print("\n")    
    
    print(result)

    if result[0] == True:
        print("\nLes signaux sont identiques (à l'erreur error près)\n" )
    else:
        print("\nL'erreur relative entre les signaux est supérieur à error sur ") 
        print("une certaine plage\n " )

    result.append(index)            
    
    return result