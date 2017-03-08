# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 15:51:39 2016

@author: Matthieu
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

def SymmetryTest(signal1, signal2, error, binary_names, name_signal1 = "", comment="ok"):
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
    n = 6 # truncation of digits in res
    result =True
    error = abs(error)
    index = []
    lin_reg = []
    sig1 = signal1.data
    sig2 = signal2.data

    if is_bool(name_signal1, binary_names):
        #The signals are categorized as boolean : we test if they are different
        for i, s in enumerate(sig1):
            if sig2[i] != s :
                result = False
                index.append(i)
        lin_reg = ["b","  -","  -","  -"] #boolean signals : no linear regression

    else :
        #The signals are 'reg'
        for i, s in enumerate(sig1):
            if s or sig2[i]: # avoid division by 0
                if abs(2*(s-sig2[i])/(abs(s)+abs(sig2[i]))) > error:
                    result = False
                    index.append(i)
            #else:
             #   if abs(sig2[i]) > error :
               #     result = [False]
                #    index.append(i)
        a, b, r_value, p_value, std_err = stats.linregress(sig1,sig2)
        lin_reg = ["c", str(a)[0:n], str(b)[0:n], str(r_value**2)] #continuous signals : linear regression parameters

    if comment != "none":
        print("\n")
        print(result)

        if result:
            print("\nLes signaux sont identiques (à l'erreur error près)\n" )
        else:
            print("\nL'erreur relative entre les signaux est supérieur à error sur ")
            print("une certaine plage\n " )

    return result, index, lin_reg

#%%

def is_bool(signal_name, signal_names_bin):
    """
    Input :

    - signal_name : a string, the name of the signal to test.

    Output :

    - Result : a boolean, is True if the input signal is known as a boolean,
    and returns False if the name is contained in the list of regulated signals (non boolean)
    """
    return signal_name in signal_names_bin

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
    names = sorted(flight.columns.values)

    result = []
    result_anomaly = []
    skip_next = False

    for i, name_i in enumerate(names[:-1]):
        if skip_next:
            skip_next = False
            # next loop, continue reduce code indent
            continue
        #Test if the current and next measures are from a different chanel
        #but equal otherwise
        next_name = names[i+1]
        if name_i[:-1] == next_name[:-1] and name_i[-1] == "A" and next_name[-1] == "B":

            signal1 = flight[name_i].iloc[:]

            signal2 = flight[next_name].iloc[:]

            #Test if anomaly between these two supposed equal signals
            res = SymmetryTest(signal1, signal2, error, name_i, "none")

            #save the main result
            result.append([name_i, next_name])
            result.append(res[0])

            if not res[0]:
                result_anomaly.append([name_i, next_name]) # signals names
                result_anomaly.append(res[1][:]) # time indexes of anomalies
                result_anomaly.append(res[2][:]) # linear fitting coeff

            #We don't need to test the next signal
            skip_next = True

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

    # Extract names of signals and sort them
    names = sorted(flight.columns.values)

    result = []
    result_anomaly = []

    #Get the signals which are from both sides and test if they are equal
    signals_with_AMSC1 = [st for st in names if 'AMSC1' in st]
    signals_with_AMSC2 = [str2.replace("AMSC1","AMSC2") for str2 in signals_with_AMSC1]

    for i, name_AMSC1 in enumerate(signals_with_AMSC1) :
        signal1 = flight[name_AMSC1].iloc[:]
        name_AMSC2 = signals_with_AMSC2[i]
        signal2 = flight[name_AMSC2].iloc[:]

        #Test if there is an anomaly between these two supposed equal signals
        res = SymmetryTest(signal1, signal2, error, name_AMSC1, "none")

        #save the main result
        result.append([name_AMSC1, name_AMSC2])
        result.append(res[0])

        if not res[0]:
            result_anomaly.append([name_AMSC1, name_AMSC2]) # signals names
            result_anomaly.append(res[1][:]) # time indexes of anomalies
            result_anomaly.append(res[2][:]) # linear fitting coeff

    return result_anomaly

#%%

def Anomalies_in_Time(result_sym, max_time_index, window_size=0.1):
    """
    Analyzes the correlation of anomalies in time : gives number of anomalies
    for some time windows.

    Inputs :

    - result_sym : results of a symmetry test which is : an array containing the
    names of the signals with anomalies (by pair), and the associated time indexes
    of anomaly occurences

    - max_time_index : an integer : the maximal time index of the flight

    - window_size : size in percentage of the flight duration of the window on
    which number of anomalies is counted (ex : 0.1 for dividing the flight in 10)
    If window_size = 0, then divides the flight with respect to the flight phases.
    By default : window_size = 0.1

    Output :

    - result : a two lignes array : the first ligne is the time indexes of the
    begining of the windows, the second ligne is the number of anomalies detected
    during the corresponding time window


    """
    result = [[], []]
    nm_anomaly = []
    n = max_time_index

    time_indexes = [result_sym[j] for j in range(len(result_sym)) if j%3 == 1]
    time_indexes_1D = []

    for j in range(1, len(result_sym), 2):
        time_indexes_1D = np.concatenate((time_indexes_1D, result_sym[j]), 0)

    time_indexes_1D = np.sort(time_indexes_1D)

    if window_size > 1:
        window_size = 1

    if window_size > 0:
        step = np.int(window_size * max_time_index)
        time_window_begining = [min(0+i*step, n) for i in range(np.int(n/step)+1)
                                if i*step != n]

        result[0] = time_window_begining

        for w, t0 in enumerate(time_window_begining):
            nm_anomaly.append(0)
            if w == len(time_window_begining)-1:
                t1 = n
            else:
                t1 = time_window_begining[w+1]
            for anomaly in range(len(time_indexes)):
                for time_anomaly in time_indexes[anomaly]:
                    if time_anomaly in range(t0, t1):
                        nm_anomaly[w] = nm_anomaly[w] + 1
                        break
        result[1] = nm_anomaly

    #***********************************
    #To do : implement calulation for the flight phases

    return result



#%%

def Analyze_results(result_sym, str_type, binary_names):
    """
    Analyzes the results given by the symmetry test (disps number of anomalies,
    if they are bool)

    Inputs :

    - result_sym : results of a symmetry test which is : an array containing the
    names of the signals with anomalies (by pair), and the associated time indexes
    of anomaly occurences

    Outputs :

    - anomalies_couples_names_sorted : list of the names of anomalies (by couple) sorted
    by their weight (number of time indexes where there is an anomaly)

    - long_sorted : number of time indexes where there is an anomaly, corresponding
    to the anomalies_couple_names_sorted

    - anomalies_lin_reg_coef_sorted : linear regression coefficients, sorted by the duration
    of the detected anomalies


    """
    anomalies_couples_names = [result_sym[j] for j in range(0, len(result_sym), 3)]
    anomalies_lin_reg_coef = [result_sym[j] for j in range(2, len(result_sym), 3)]

    # On peut voir si les anomalies sont des booleans ou des signaux regulés
    name_anomaly = [anomalies_couples_names[j][0] for j in range(len(anomalies_couples_names))]
    is_bool_anomaly = [is_bool(j, binary_names) for j in name_anomaly]


    if str_type == 'channel':
        print("Il y a {} anomalies detectees entre channels"
              .format(len(anomalies_couples_names)))

        if False in is_bool_anomaly:
            if True in is_bool_anomaly:
                print("Pour channels A/B : Les anomalies sont réparties entre booléans et signaux régulés")
            else:
                print("Pour channels A/B : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
        else:
            print("Pour channels A/B : Il n'y a que des anomalies sur des booléans")
    else:

        print("Il y a {} anomalies detectees sur la symetrie laterale"
              .format(len(anomalies_couples_names)))

        if False in is_bool_anomaly:
            if True in is_bool_anomaly:
                print("Pour symetrie laterale : Les anomalies sont réparties entre booléans et signaux régulés")
            else:
                print("Pour symetrie laterale : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
        else:
            print("Pour symetrie laterale : Il n'y a que des anomalies sur des booléans")


    #Statistiques anomalies
    ind = [result_sym[j] for j in range(1, len(result_sym), 3)] # time indexes
    long = [len(ind[i]) for i in range(len(ind))]
    long_np = np.array(long);


    # Ordonner les anomalies dans l'ordre decroissant
    sorted_ind = np.argsort(-long_np)

    long_sorted = long_np[sorted_ind]

    anomalies_couples_names_sorted = [anomalies_couples_names[i] for i in sorted_ind]
    anomalies_lin_reg_coef_sorted = [anomalies_lin_reg_coef[i] for i in sorted_ind]

    return anomalies_couples_names_sorted, long_sorted, anomalies_lin_reg_coef_sorted

#%%
def write_in_file(path, name_flight, list_anomaly, duration_anomaly, lin_reg_coef, error, is_channel) :

    """
    Writes the anomaly results into a txt file

    Inputs :

    - path : string, the path of the file

    - name_flight : string, name of the flight

    - list_anomaly : list of the names of anomalies

    - duration_anomaly : list of the duration of detected anomaly

    - lin_reg_coef : list of the linear regression coefficients

    - error : relative error used for the anomaly detection

    - is_channel : bool to know whether the anomalies are from channel or lateral

    """

    longs = [len(list_anomaly[i][0]) for i in range(len(list_anomaly))]
    taille_max = max(longs)+2

    fichier = open(path, "a")

    if is_channel == 1 :

       fichier.write("\n Résultats de symmétrie du vol : " + name_flight+ "\n\n")
       fichier.write("\n Erreur relative utilisée : " + str(error)+"\n")
       fichier.write("\n Résultats asymetrie CHANNEL : "+str(len(list_anomaly))+" paires de signaux anormaux. ")
       fichier.write("\n (le lateral est plus bas) \n\n\n ")
       fichier.write("\n Format : [ Anomalie 1/2 ; Anomalie 2/2] : temps de vol anormal (en pourcentage du temps de vol total) | Coefficients de regression linéaire : y = ax+b ['b'(bool) or 'c' (continu),a, b, r^2] \n \n")
       for i in range(len(list_anomaly)):
           fichier.write("\n [\t" + list_anomaly[i][0].ljust(taille_max) + " ; \t" + list_anomaly[i][1].ljust(taille_max) + "\t]  :  "+ str(100*duration_anomaly[i])[0:5] )
           fichier.write(" | \t[ '"+ lin_reg_coef[i][0]+" ', "+lin_reg_coef[i][1].ljust(8)+", "+lin_reg_coef[i][2].ljust(8)+", "+lin_reg_coef[i][3].ljust(12)+"\t]")

    else:
        fichier.write("\n ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n \n")
        fichier.write("\n Résultats asymetrie LATERAL : "+str(len(list_anomaly))+" paires de signaux anormaux.\n ")

        fichier.write("\n Format : [ Anomalie 1/2 ; Anomalie 2/2] : temps de vol anormal (en pourcentage du temps de vol total) | Coefficients de regression linéaire : y = ax+b ['b'(bool) or 'c' (continu),a, b, r^2] \n \n")
        for i in range(len(list_anomaly)):
            fichier.write("\n [\t" + list_anomaly[i][0].ljust(taille_max) + " ; \t" + list_anomaly[i][1].ljust(taille_max) + "\t]  :  "+ str(100*duration_anomaly[i])[0:5] )
            fichier.write(" | \t[ '"+ lin_reg_coef[i][0]+" ', "+lin_reg_coef[i][1].ljust(8)+", "+lin_reg_coef[i][2].ljust(8)+", "+lin_reg_coef[i][3].ljust(12)+"\t]")


    fichier.close()

#%%

def write_in_csv(path, list_anomaly, duration_anomaly, lin_reg_coef) :

    """
    Writes the anomaly results into a csv file

    Inputs :

    - path : string, the path of the file

    - list_anomaly : list of the names of anomalies

    - duration_anomaly : list of the duration of detected anomaly

    - lin_reg_coef : list of the linear regression coefficients


    """
    rapport_anomalie = {}
    rapport_anomalie["Signal A"] = [a[0] for a in list_anomaly]
    rapport_anomalie["Signal B"] = [a[1] for a in list_anomaly]
    rapport_anomalie["Anomaly duration (%)"] = [str(100*a)[0:5] for a in duration_anomaly]
    rapport_anomalie["Type"] = [a[0] for a in lin_reg_coef]
    rapport_anomalie["Lin Reg Slope"] = [a[1] for a in lin_reg_coef]
    rapport_anomalie["Lin Reg Intercept"] = [a[2] for a in lin_reg_coef]
    rapport_anomalie["Lin Reg R2"] = [a[3] for a in lin_reg_coef]
    columns = ["Type", "Signal A", "Signal B", "Anomaly duration (%)",
               "Lin Reg Slope", "Lin Reg Intercept", "Lin Reg R2"]
    pd.DataFrame(rapport_anomalie).to_csv(path+".csv", columns=columns,
                                          index_label="Id")

#%%

if __name__ == "__main__":
    import sys,os
    sys.path.append(os.path.abspath('..'))
    from dataProcessing.parser import txt_parser
    path = '../pie_data/'
    #raw_flight = txt_parser(path+"data1.txt")
    raw_flight = txt_parser(path+"E190-E2_20001_0090_29867_54229_request.txt")

    error = 0.01 # marge d'erreur relative acceptee (0.01 correspond à 1% de marge)

    #----------------------------------------------
    ### How to use this result ? -> example
    #..............................................
    ## With Channels
    result_channel = Symmetry_Channels_One_Flight(raw_flight,error)


    #names of the couples supposed equal by symmetry but actuelly different
    anomalies_couples_names = [result_channel[j] for j in range(len(result_channel)) if j%3 == 0]
    print("Il y a " + str(len(anomalies_couples_names)) +" anomalies detectees entre channels" )

    #Affichage de l'avant derniere anomalie
    s1 = raw_flight[anomalies_couples_names[-2][0]]
    s2 = raw_flight[anomalies_couples_names[-2][1]]
    s1.plot()
    s2.plot()

    #On peut voir si les anomalies sont des booleans ou des signaux regulés
    name_anomaly = [anomalies_couples_names[j][0] for j in range(len(anomalies_couples_names))]
    is_bool_anomaly = [is_bool(j, binary_names) for j in name_anomaly]
    if False in is_bool_anomaly:
        if True in is_bool_anomaly:
            print("Pour channels A/B : Les anomalies sont réparties entre booléans et signaux régulés")
        else :
            print("Pour channels A/B : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
    else :
        print("Pour channels A/B : Il n'y a que des anomalies sur des booléans")

    #..............................................
    ## With lateral Symmetry

    result_lat = Symmetry_Lateral_One_Flight(raw_flight,error)
    #names of the couples supposed equal by symmetry but actuelly different
    anomalies_lat_couples_names = [result_lat[j] for j in range(len(result_lat)) if j%3 == 0]
    print("Il y a " + str(len(anomalies_lat_couples_names)) +" anomalies detectees sur la symetrie laterale" )

    #Affichage de l'avant derniere anomalie
    s1 = raw_flight[anomalies_lat_couples_names[-2][0]]
    s2 = raw_flight[anomalies_lat_couples_names[-2][1]]
    s1.plot()
    s2.plot()

    #On peut voir si les anomalies sont des booleans ou des signaux regulés
    name_anomaly = [anomalies_lat_couples_names[j] for j in range(len(anomalies_lat_couples_names)) if j%3 == 0 ]
    is_bool_anomaly = [is_bool(j, binary_names) for j in name_anomaly]
    if False in is_bool_anomaly:
        if True in is_bool_anomaly:
            print("Pour symetrie laterale : Les anomalies sont réparties entre booléans et signaux régulés")
        else :
            print("Pour symetrie laterale : Il n'y a que des anomalies sur des non booleans (signaux regulés)")
    else :
        print("Pour symetrie laterale : Il n'y a que des anomalies sur des booléans")


    #Plot du nombre d'anomalies en fonction du temps
    nb_anomaly_time_ch = Anomalies_in_Time(result_channel, len(s1), 0.01)
    plt.figure(0)
    plt.plot(nb_anomaly_time_ch[0],nb_anomaly_time_ch[1],'ro')

    nb_anomaly_time_lat = Anomalies_in_Time(result_lat, len(s1), 0.1)
    plt.figure(1)
    plt.plot(nb_anomaly_time_lat[0],nb_anomaly_time_lat[1],'ro')


    #Statistiques anomalies
    ind_lat = [result_lat[j] for j in range(len(result_lat)) if j%3 == 1]
    long = [len(ind_lat[i]) for i in range(len(ind_lat))]
    longr = [i/len(s1) for i in long] # r pour relatif (en pourcentage de temps de vol)
    np.std(longr)  # STD des temps d'anomalies en pourcentage de temps de vol
    np.mean(longr) # Moyenne des temps d'anomalies en pourcentage de temps de vol
    longr_95 = [i for i in longr if i > 0.95]
    len(longr_95) # Nombre de signaux anormaux pendant au moins 95% du vol

    if 0 :
        from dataProcessing.plotter import Plotter
        p = Plotter()
        flight2 = txt_parser(path+"E190-E2_20001_0090_29867_54229_request.txt")
        p.set_data(flight2)
        p.plot(['ACS_PBIT_ENABLED_AMSC1_CHA', 'ACS_PBIT_ENABLED_AMSC2_CHA'])
