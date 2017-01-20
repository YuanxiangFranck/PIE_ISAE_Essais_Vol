# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 15:51:39 2016

@author: Matthieu
"""

import numpy as np

def SymmetryTest(signal1, signal2, error, name_signal1 = "", comment="ok"):
    """
    
    
    Inputs : 
    
    - signal1, signal2 : two signals of the class SignalData to compare 
    (generally signal1 -> "...CHA", and signal2 -> "...CHB"  )
    
    - error : the result will be False if there is at least one value which is 
    out of the relative error box 
    
    - [name_signal1] : optional, a string, the name of the first input. Allows
    the algorithm to check if the inputs are boolean or not (from specifications)
    By defaut, consider the signal as non boolean.
    
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
    
    if is_bool(name_signal1) :
        #The signals are categorized as boolean : we test if they are different
        for i,s in enumerate(sig1):
            if sig2[i] != s :
                result = [False]
                index.append(i)
    else :
        #The signals are 'reg' 
        for i,s in enumerate(sig1):
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
    
#%%
    
def is_bool(signal_name) :
        
    """
    
    Input : 
    
    - signal_name : a string, the name of the signal to test. 
    
    Output :
    
    - Result : a boolean, is True if the input signal is known as a boolean, 
    and returns False if the name is contained in the list of regulated signals (non boolean)
    """
    
    result = True
    
    # list of the names of regulated signals (continuous)
    reg_signal_names = \
    ['CPCS_CABIN_PRESS_AMSC1_CHA',
    'CPCS_CABIN_PRESS_AMSC1_CHB',
    'CPCS_CABIN_PRESS_AMSC2_CHA',
    'CPCS_CABIN_PRESS_AMSC2_CHB',
    'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC1_CHA',
    'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC1_CHB',
    'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC2_CHA',
    'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC2_CHB',
    'ACS_MIX_TEMP_AMSC1_CHA',
    'ACS_MIX_TEMP_AMSC1_CHB',
    'ACS_MIX_TEMP_AMSC2_CHA',
    'ACS_MIX_TEMP_AMSC2_CHB',
    'ACS_ZONE1_DUCT_TEMP_AMSC1_CHA',
    'ACS_ZONE1_DUCT_TEMP_AMSC1_CHB',
    'ACS_ZONE1_DUCT_TEMP_AMSC2_CHA',
    'ACS_ZONE1_DUCT_TEMP_AMSC2_CHB',
    'ACS_ZONE2_DUCT_TEMP_AMSC1_CHA',
    'ACS_ZONE2_DUCT_TEMP_AMSC1_CHB',
    'ACS_ZONE2_DUCT_TEMP_AMSC2_CHA',
    'ACS_ZONE2_DUCT_TEMP_AMSC2_CHB',
    'ACS_ZONE1_TEMP_AMSC1_CHA',
    'ACS_ZONE1_TEMP_AMSC1_CHB',
    'ACS_ZONE1_TEMP_AMSC2_CHA',
    'ACS_ZONE1_TEMP_AMSC2_CHB',
    'ACS_ZONE2_TEMP_AMSC2_CHA',
    'ACS_ZONE2_TEMP_AMSC2_CHB',
    'BLEED_OUT_PRESS_AMSC1_CHA',
    'BLEED_OUT_PRESS_AMSC1_CHB',
    'BLEED_OUT_PRESS_AMSC2_CHA',
    'BLEED_OUT_PRESS_AMSC2_CHB',
    'BLEED_OUT_TEMP_AMSC1_CHA',
    'BLEED_OUT_TEMP_AMSC1_CHB',
    'BLEED_OUT_TEMP_AMSC2_CHA',
    'BLEED_OUT_TEMP_AMSC2_CHB',
    'APS_OUT_PRESS_AMSC1_CHA',
    'APS_OUT_PRESS_AMSC1_CHB',
    'APS_OUT_PRESS_AMSC2_CHA',
    'APS_OUT_PRESS_AMSC2_CHB',
    'APS_OUT_TEMP_AMSC1_CHA',
    'APS_OUT_TEMP_AMSC1_CHB',
    'APS_OUT_TEMP_AMSC2_CHA',
    'APS_OUT_TEMP_AMSC2_CHB',
    'WAI_CONTROLLING_PRESS_AMSC1_CHA',
    'WAI_CONTROLLING_PRESS_AMSC1_CHB',
    'WAI_CONTROLLING_PRESS_AMSC2_CHA',
    'WAI_CONTROLLING_PRESS_AMSC2_CHB',
    'WAI_OPP_CONTROLLING_PRESS_AMSC1_CHA',
    'WAI_OPP_CONTROLLING_PRESS_AMSC1_CHB',
    'WAI_OPP_CONTROLLING_PRESS_AMSC2_CHA',
    'WAI_OPP_CONTROLLING_PRESS_AMSC2_CHB']
    
    if signal_name in reg_signal_names :
        result = False
    
    return result
    
    #%%
    
def Symmetry_Channels_One_Flight(flight, error):
        
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
                res = SymmetryTest(signal1, signal2, error, name_i, "none")

                
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



#%%
    
def Symmetry_Lateral_One_Flight(flight, error):
        
    """
    Find the symmetry problems in a flight by comparing the right and left side for each measure of a flight.        
    
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
  
    #Get the signals which are from both sides and test if they are equal
    signals_with_AMSC1 = [st for st in names if 'AMSC1' in st]
    signals_with_AMSC2 = [str2.replace("AMSC1","AMSC2") for str2 in signals_with_AMSC1] 
   
    for i,name_AMSC1 in enumerate(signals_with_AMSC1) :
        signal1 = flight[name_AMSC1].iloc[:]
        name_AMSC2 = signals_with_AMSC2[i]
        signal2 = flight[name_AMSC2].iloc[:]
        
        #Test if there is an anomaly between these two supposed equal signals
        res = SymmetryTest(signal1, signal2, error, name_AMSC1, "none")
        
        #save the main result
        result.append([name_AMSC1, name_AMSC2])
        result.append(res[0])
        
        if res[0] == False :
            result_anomaly.append([name_AMSC1, name_AMSC2])
            result_anomaly.append(res[1][:])
                                
        
    return result_anomaly
    
#%%
    
    
if __name__ == "__main__":
    import sys,os
    sys.path.append(os.path.abspath('..'))
    from dataProcessing.parser import txt_parser
    path = '../pie_data/'
    flight = txt_parser(path+"data1.txt")
        
    error = 0.01 # marge d'erreur relative acceptee (0.01 correspond à 1% de marge)
    
    #----------------------------------------------
    ### How to use this result ? -> example
    #..............................................
    ## With Channels     
    result_channel = Symmetry_Channels_One_Flight(flight,error)

    
    #names of the couples supposed equal by symmetry but actuelly different
    anomalies_couples_names = [result_channel[j] for j in range(len(result_channel)) if j%2 == 0]
    print("Il y a " + str(len(anomalies_couples_names)) +" anomalies detectees entre channels" )
    
    #Affichage de l'avant derniere anomalie 
    s1 = flight[anomalies_couples_names[-2][0]]
    s2 = flight[anomalies_couples_names[-2][1]]
    s1.plot()
    s2.plot()
    
    #On peut voir si les anomalies sont des booleans ou des signaux regulés
    name_anomaly = [anomalies_couples_names[j] for j in range(len(anomalies_couples_names)) if j%2 == 0 ]
    is_bool_anomaly = [is_bool(j) for j in name_anomaly]
    if False in is_bool_anomaly:
        if True in is_bool_anomaly:
            print("Pour channels A/B : Les anomalies sont réparties entre booléans et signaux régulés")
        else :
            print("Pour channels A/B : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
    else :
        print("Pour channels A/B : Il n'y a que des anomalies sur des booléans")
        
     #..............................................
     ## With lateral Symmetry 
    
    result_sym = Symmetry_Lateral_One_Flight(flight,error)
    #names of the couples supposed equal by symmetry but actuelly different
    anomalies_couples_names = [result_sym[j] for j in range(len(result_sym)) if j%2 == 0]
    print("Il y a " + str(len(anomalies_couples_names)) +" anomalies detectees sur la symetrie laterale" )
    
    #Affichage de l'avant derniere anomalie 
    s1 = flight[anomalies_couples_names[-2][0]]
    s2 = flight[anomalies_couples_names[-2][1]]
    s1.plot()
    s2.plot()
    
    #On peut voir si les anomalies sont des booleans ou des signaux regulés
    name_anomaly = [anomalies_couples_names[j] for j in range(len(anomalies_couples_names)) if j%2 == 0 ]
    is_bool_anomaly = [is_bool(j) for j in name_anomaly]
    if False in is_bool_anomaly:
        if True in is_bool_anomaly:
            print("Pour symetrie laterale : Les anomalies sont réparties entre booléans et signaux régulés")
        else :
            print("Pour symetrie laterale : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
    else :
        print("Pour symetrie laterale : Il n'y a que des anomalies sur des booléans")
        