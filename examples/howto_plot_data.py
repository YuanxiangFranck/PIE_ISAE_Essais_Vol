# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 15:34:24 2016

@author: Florent

Template pour tracer un signal avec le plotter

Pour afficher les plots en mode fenêtre, taper
%matplotlib qt
dans votre console ipython, et
%matplotlib inline
en mode intégré.
"""
import sys, os
sys.path.append(os.path.abspath('..'))
from dataProcessing.plotter import Plotter



#%%

"""
Vol XXXXX
(préciser le numéro du vol étudié)

"""

## 1. Chargement du fichier de données et création du Plotter

# Chemin relatif vers le fichier txt de données
data_path = '../../pie_data/data1.txt'
# pour le vol FT53398

# création du Plotter
monPlotter = Plotter(data_path)

## 2. Tracé


# noms des signaux à plotter (un seul ou plusieurs signaux dans la liste)
signal_names = ['BLEED_OUT_TEMP_AMSC1_CHA', 'BLEED_OUT_TEMP_AMSC1_CHB']

# Plotter les signaux de la liste par rapport au temps :
monPlotter.plot(signal_names[1:])
# # Plotter SIG1 par rapport à SIG2 :
# monPlotter.plot_data(signal_names[0], signal_names[1])
# # seulement si len(signal_names) == 2
