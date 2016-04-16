# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 20:02:26 2014

@author: Clément Saintier

This file defines configuration options that will be used throughout the programm
Use "import config as c" and "c.WORKING_DIR" to access them.
"""
import os

#directory where log.txt and audio files and such will be stored
WORKING_DIR = os.getcwd() + "/"

#How many sample should we cut at the beginning when recording ?
#Usefull when a microphone sends a bump when turning on
CUT = 11025

#Method used to extract bumptimes out of signals
#can be : "threshold" or "correlation" ... <work in progress>
METHOD = "threshold"

    #if method used is threshold, how should the threshold be fixed ?
    #values can be "defined", "maxlevel", "average"
THRESHOLD_AUTOSET = "maxlevel"

        #if the threshold has to be defined you, what should it be ?
THRESHOLD_VALUE = 5000

        #if the threshold has to be set from the maxlevel, what factor has
        #to be multiplied to the maxlevel to yield the threshold ?
MAX_LEVEL_MULTIP = 0.25

        #if the threshold has to be set from the average, what factor has to be
        #multiplied to the average to yield the threshold ?
AVERAGE_LEVEL_MULTIP = 8

    #if the method used is threshold, this is the maximum length in sample of a
    #bump, to be used with the threshold method, to avoid analysing the same
    #bump as 2 separate bumps
MAX_BUMP_LENGTH = 0.1*44100

    #if the method used is correlate, what step should be used in the correlation function ? (in sample)
CORRELATION_STEP = 20

    #if method used is correlation, should we put everything in positive ? (result = abs(result)=
CORRELATION_ABS = 0

#What method should be used to compare the given rythm to the key rythm ?
#values can be "simple" or "complex"
KEY_METHOD = "complex"

#if key_method is "simple" : maximal difference between each values in key and trial
TOLERANCE = 50

#if key_method is "complex" : maximal gap between key and trial
MAX_GAP = 0.00354416282462185000

#to analyse a bump excerpt (threshold_noise = max_noise*c.START_TH_MULTIP) threshold_noise being the level at which the bump is considered as "starting"
START_TH_MULTIP = 4

THRESHOLD_INTENSITIES_MULTIP = 0.25

#when Multiplying signals, what should the result be divided by ? (Prevents overflowing values)
DIVISOR = 1000


#######################
##TEST RELATED CONFIG##
###################################################

#Should we display the wave when extracting bumptimes?
SHOW_WAVE = 0

#should we display the threshold on the same graph ?
SHOW_TH = 1

#should we log & display the exctracted bumptimes ?
SHOW_BT = 1

#should we print the dected gap between tested rythm and key, when using complex comparison method ?
SHOW_GAP = 1

#how much time should interface() record ?
#0 = ask everytime
REC_TIME = 4

#should we log (with level 1) the gaps ?
LOG_GAPS = 1



#######TODO LIST########
##ajouter a la class recordding la possibilité de créer une instance directement en enregistrant, pour éviter d'avoir a définir l'enregistrement d'abbord pour ensuite proceder a record()
##créer une classe "function" qui représente une fonction f(x) = y avec x et y on s'en fout ce que c'est. au lieu d'avoir data et rate, on aurait data {Xi : Yi} un dictionnaire.
##écrire des fonctions plus spécifiques bordel de merde ! get_bt_threshold ? non ! faire une fonction "get_abscissa_whose_ordinates_are_above(threshold)", puis dans get_bt_threshold, mettre le code qui choisis le threshold, puis "get_abscissa_whose..."