# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 15:51:39 2016

@author: Matthieu
"""

import numpy as np

def SymmetryTest(signal1, signal2, error, comment="ok"):
    """
    
    
    Inputs : 
    
    - signal1, signal2 : two signals of the class SignalData to compare 
    (generally signal1 -> "...CHA", and signal2 -> "...CHB"  )
    
    - error : the result will be False if there is at least one value which is 
    out of the relative error box 
    
    - [comment] : otpional, a string, if equals 'none' then don't print any result,
    prints the result if nothing is specified
    
    Output :
    
    - Result : an array, wich first value is boolean, indicates if the two imput 
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
                
    if comment != "none" :
        print("\n")
        print(result)

        if result[0] == True:
            print("\nLes signaux sont identiques (à l'erreur error près)\n" )
        else:
            print("\nL'erreur relative entre les signaux est supérieur à error sur ") 
            print("une certaine plage\n " )

    result.append(index)            
    
    return result
    
    
    
def Symmetry_One_Flight(flight, error):
        
    """
    Find the symmetry problems in a flight by comparing both channels A 
    and B for each measure of a flight.        
    
    Inputs : 

    - flight : must have been parsed by txt_parser. Contains all the signals
    of one flight

    - error : relative error accepted for the detection of anomalies between
    two signals which should have been equal


    Output :

    - result_anomaly : Contains the names of the supposed equal signals wich are 
    actually different. Contains as well the indexes where the differences were 
    found
    The names are in result_anomaly[2*i] and the indexes in result_anomaly[2*i+1]
    with i <= 0
        """

    #flight = txt_parser(path+str_flight)  

    # Extract names of signals and sort them        
    names = flight.columns.values 
    names.sort()
    
    result = []
    result_anomaly = []
    next = 1

    
    for i,name_i in enumerate(names[:-1]):
        if next == 0 :
            next = 1
        else :
            #Test if the current and next measures are from a different chanel
            #but equal otherwise
            if (name_i[0:-1] == names[i+1][0:-1]) and (name_i[-1] == "A") and (names[i+1][-1] == "B"):
                
                signal1 = flight[name_i].iloc[:]
                
                signal2 = flight[names[i+1]].iloc[:]
                
                
                #Test if anomaly between these two supposed equal signals
                res = SymmetryTest(signal1, signal2, error, "none")

                
                #save the main result
                result.append([name_i, names[i+1]])
                result.append(res[0])
                
                if res[0] == False :
                    result_anomaly.append([name_i, names[i+1]])
                    result_anomaly.append(res[1][:])
                    
            
                #We don't need to test the next signal
                next = 0
            
            else:
                next = 1
        
        
    return result_anomaly

    
if __name__ == "__main__":
    import sys,os
    sys.path.append(os.path.abspath('..'))
    from dataProcessing.parser import txt_parser
    path = '../pie_data/'
    flight = txt_parser(path+"data1.txt")
        
    error = 0.01 # marge d'erreur relative acceptee (0.01 correspond à 1% de marge)
    result = Symmetry_One_Flight(flight,error)

    ##How to use this result ? -> example 
    #names of the couples supposed equal by symmetry but actuelly different
    anomalies_couples_names = [result[j] for j in range(len(result)) if j%2 == 0]
    print("Il y a " + str(len(anomalies_couples_names)) +" anomalies detectees" )
    
    #Affichage de l'avant derniere anomalie 
    s1 = flight[anomalies_couples_names[-2][0]]
    s2 = flight[anomalies_couples_names[-2][1]]
    s1.plot()
    s2.plot()