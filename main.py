# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 23:19:36 2014

@author: Clément Saintier
"""

from scipy.io.wavfile import *          #This only works with "from _ import *"
import wave                             #This only works with "import _"

import numpy
import pylab
import pyaudio                          #This only works with "import _"

import config as c

from ClassRecording import *
from ClassSignal import *
from ClassRythm import *
from ClassCharacteristics import *
from verbose import *

def correlation_spe(s1, s2, zero_pos, step, range_):
    """  |---------------------------------------------> passing time
    s1:  +-+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+ (analyzed signal)
    s2:         -+-+-+-+-+-+-+-+-                   (signal we're looking for)
                        ^
                        |
                     zero_pos
                   s2 will be moved step*range_ to left to start with,
                   then step*(range_-1) ... then 0 (no delay), then step*1 to
                   the right, then step*2 ... then step*range_.
                that means :
                s2 shall be delayed by step*tau with tau from -range_ to range_

    each time s2 is delayed, we calculate de product of the two (overlapping)
    signals, from wich we take the average, and each value shall be stored in a
    list in order to interpret the graph of "tau -> average(tau)"

    step zero_pos andstep are times, expressed in "samples"
    range_ is a multiplicator for step
    before using this function, one has to calculate what step and range_ to take
    to achieve what they want"""

    if not isinstance(s1, Signal):
        verbose("analyzed signal given isn't a signal", 1)
        quit()
    if not isinstance(s2, Signal):
        verbose("searched signal given isn't a signal", 1)
        quit()
    if zero_pos-(range_*step)-(len(s2.data)//2) < 0 or zero_pos+(range_*step)+(len(s2.data)//2) > len(s1.data):
        verbose("step and range_ are such as the searched signal happen to overlap emptyness, more info in the code's commentary", 1)
        ##  s1:  +-+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+???????
        ##  s2:                                       -+-+-+-+-+-+-+-+-
        ##                                                     ^
        ##                                zero_pos+range_*step |
        quit()

    averages = []
    for i in range(-range_, range_+1): ##for range_ = 3, i will take [-3,-2,-1,0,1,2,3]
        cur_tau = i*step
        cur_start = zero_pos+cur_tau-(len(s2.data)//2)
        cur_end =   zero_pos+cur_tau+(len(s2.data)//2)
        cur_s1 = s1.get_truncated(cur_start, cur_end)
        cur_resul = cur_s1*s2
        averages.append(cur_resul.get_average())

    pylab.figure(2)
    pylab.plot(averages)
    pylab.show()

    return 0

def correlation(s1, s2, step):
    """  |---------------------------------------------> passing time
    s1:  +-+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+ (analyzed signal)
    s2:         -+-+-+-+-+-+-+-+-                   (signal we're looking for)
    """

    if not isinstance(s1, Signal):
        verbose("analyzed signal given isn't a signal", 1)
        quit()
    if not isinstance(s2, Signal):
        verbose("searched signal given isn't a signal", 1)
        quit()

    averages = []
    start_times = []
    cur_start = 0
    while cur_start+len(s2) < len(s1):
        cur_end = cur_start + len(s2)
        cur_s1 = s1.get_truncated(cur_start,cur_end)
        cur_resul = cur_s1*s2
        averages.append(cur_resul.get_average(False))
        start_times.append(cur_start)
        cur_start += step

    pylab.figure(2)
    pylab.plot(start_times, averages)
    pylab.show()

def tests_en_serie():
    r_temp = Recording("experience ")
    r_clee = Recording("clee")
    print("tests en série")

    print("----------------------------------------------------------------")
    input("OK ?")
    r_clee.record(4)
    s_clee = Signal("clee", r_clee)
    ry_clee = Rythm("clee", s_clee)
    print(ry_clee)

    print("----------------------------------------------------------------")
    input("OK ?")
    i = 0
    while(1):
        print("-------")
        print("|  "+str(i)+"  |")
        print("-------")
        r_temp.record(4)
        s_temp = Signal("temp", r_temp)
        ry_temp = Rythm("temp", s_temp)

        print(str(ry_temp == ry_clee))

        # print("VOTRE RYTHME :")
        # verbose(ry_temp,1)
        i += 1


def interface():
    print("projet python v3")
    r_temp = Recording("clef")
    r_essai = Recording("essai")
    ry_temp = 0
    ry_clef = 0
    done = False
    while not done:
        print("----------------------------------------------------------------")
        print("Que faire ?")
        print("0 - quitter")
        print("1 - enregistrer une clef")
        print("2 - essayer d'ouvrir la porte")
        print("3 - voir la clef")
        print("4 - voir ou sont sauvegardés les fichier log.txt et les enregistrements")
        choix = int(input())
        if choix == 1:
            duree =c.REC_TIME
            if not duree:
                duree = int(input("enregistrer pendant combien de temps ? (en secondes)"))
            r_temp.record(duree)
            s_temp = Signal("temp", r_temp)
            ry_temp = Rythm("temp", s_temp)
            print("VOTRE RYTHME :")
            print(ry_temp)
            print("Voulez vous la conserver comme clef ? (0 - non / 1 - oui)")
            choix = int(input())
            if choix:
                ry_clef = ry_temp
                print("rythme enregistré comme clef")
            else:
                print("rythme abandonné, la clef définie n'a pas été modifiée")
        elif choix == 2:
            if ry_clef == 0:
                print("Il n'y a pas de clef définie")
            else:
                duree =c.REC_TIME
                if not duree:
                    duree = int(input("enregistrer pendant combien de temps ? (en secondes)"))
                r_essai.record(duree)
                ry_essai = Rythm("essai", Signal("essai", r_essai))
                print(ry_essai)
                if ry_essai == ry_clef:
                    print("CODE BON : porte ouverte")
                else:
                    print("MAUVAIS CODE : porte fermée")
        elif choix == 3:
            if ry_clef == 0:
                print("Il n'y a pas de clef définie")
            else:
                print(ry_clef)
        elif choix == 4:
            print(c.WORKING_DIR)
        elif choix == 0:
            done = 1



# r_a = Recording("a")
# r_a.load_data()
# s_a = Signal("a", r_a)

# r_a_m1 = Recording("a-1")
# r_a_m1.load_data()
# s_a_m1 = Signal("a_m1", r_a_m1)

# r_a_p1 = Recording("a+1")
# r_a_p1.load_data()
# s_a_p1 = Signal("a_p1", r_a_p1)

# print(s_a)
# print(s_a_m1)
# print(s_a_p1)
# print(s_a * s_a_m1)
# print(s_a * s_a)
# print(s_a * s_a_p1)


interface()
#tests_en_serie()

# r_bump = Recording("bump")
# r_bump.load_data()
# s_bump = Signal("bump", r_bump)

# r_essai = Recording("essai")
# r_essai.record(4)
# s_essai = Signal("essai", r_essai)
# ry_essai = Rythm("ry_essai", s_essai, s_bump)

# print(ry_essai)

#DEMO DERIVATE
# y = []
# for i in range(0, 100):
   # y.append(numpy.cos(0.5*i))

# s_carre = Signal("fonction cos", y)
# print(s_carre.get_symbol_change_abscissa())

##DEMO DERIVATE
# y = []
# for i in range(0, 100):
    # y.append(i*3)

# s_carre = Signal("fonction carrée", y)
# s_derive = s_carre.get_derivated()
# print(s_derive)

##DEMO CHARACTERISTICS
# input("ok?")
# r_noise = Recording("noise")
# r_noise.record(3)
# s_noise = Signal("test", r_noise)
# input("ok?")
# r_bump = Recording("bump")
# r_bump.record(3)
# s_bump = Signal("bump", r_bump)
# print(s_noise)
# print(s_bump)
# a = Characteristics("ordonée",s_noise,s_bump)
# print(a.s_ordonate)
# print(a.s_abscissa)
# char1 = Characteristics("qsdf", s_noise, s_bump)
# print(char1.get_bump_length())

##DEMO FFT
# s_test = Signal("test", "vvv.wav")
# a,b = s_test.get_spectrum()
# print(s_test)
# pylab.figure(1)
# pylab.plot(a,b,"x")
# pylab.show()

##DEMO CHARACTERISTICS 2
#input("enregistrez le bruit ambiant :")
#r_noise = Recording("noise")
#r_noise.record(3)
#s_noise = Signal("test", r_noise)
#input("enregistrez UN accoup :")
#r_bump = Recording("bump")
#r_bump.record(3)
#s_bump = Signal("bump", r_bump)
#
## print(s_noise)
## print(s_bump)
## s_bump.show_spectrum()
#
#a = Characteristics("char1", s_noise, s_bump)
#print(a.s_clean_bump)
#a.list_freq_and_intensities_caracteristics()
## print ("fréquance maximale est:" + str(a.list_freq_and_intensities_caracteristics()))
## print ("liste des fréq et intensités cara:" + str(a.list_freq_and_intensities_caracteristics()))
#pylab.figure()
#x,y=a.list_freq_and_intensities_caracteristics()
#pylab.plot(y, x , "b")
#
#pylab.show()
#a.show_clean_bump_spectrum()

##DEMONSTRATION correlation 6
# r_essai = Recording("enregistrement typique 6")
# r_essai.load_data()
# s_essai = Signal("essai",r_essai)
# s_a_chercher = s_essai.get_truncated(43370,45331)
# print(s_essai)
# print(s_a_chercher)
# correlation(s_essai,s_a_chercher, 100)

#DEMONSTRATION correlation 7
# r_essai = Recording("enregistrement typique 7")
# r_essai.load_data()
# s_essai = Signal("essai",r_essai)
# s_a_chercher = s_essai.get_truncated(58500,66000)
# print(s_essai)
# print(s_a_chercher)
# correlation(s_essai,s_a_chercher,100)

#DEMONSTRATION correlation 8
# r_essai = Recording("enregistrement typique 8")
# r_essai.load_data()
# s_essai = Signal("essai",r_essai)
# s_a_chercher = s_essai.get_truncated(139450,144263)
# print(s_essai)
# print(s_a_chercher)
# correlation(s_essai,s_a_chercher,100)

#DEMONSTRATION correlation 9
# r_essai = Recording("enregistrement typique 9")
# r_essai.load_data()
# s_essai = Signal("essai",r_essai)
# s_a_chercher = s_essai.get_truncated(117584,123641)
# print(s_essai)
# print(s_a_chercher)
# correlation(s_essai,s_a_chercher,100)

#DEMONSTRATION correlation 11
# r_essai = Recording("enregistrement typique 11")
# r_essai.load_data()
# s_essai = Signal("essai",r_essai)
# s_a_chercher = s_essai.get_truncated(52339,54260)
# print(s_essai)
# print(s_a_chercher)
# correlation(s_essai,s_a_chercher,10)

#DEMO ENVELOPPE
# r_essai = Recording("enregistrement typique 6")
# r_essai.load_data()
# s_essai = Signal("essai", r_essai)
# a,b = s_essai.get_enveloppe(1000)

# pylab.clf()
# pylab.figure(1)
# pylab.subplot(2,1,1)
# pylab.plot(s_essai.data, "r")
# pylab.subplot(2,1,2)
# pylab.plot(a,b,"r")
# pylab.show()
