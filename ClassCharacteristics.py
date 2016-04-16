# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 20:02:26 2014

@author: Sindarus&Magda
"""

from scipy.io.wavfile import *          #This only works with "from _ import *"
import wave                             #This only works with "import _"

import numpy
import pylab
import pyaudio                          #This only works with "import _"

import config as c

from verbose import *
from ClassSignal import *


class Characteristics:
    """
    la durée, l'ordonnée max et abscisse correspondante, fréquence fondamentale
    s_noise, s_bump, s_clean_bump
    """
    def __init__(self, title, s_noise, s_bump1, s_bump2, s_bump3):
        """
        s_bump1, 2 and 3 are the raw recording of the bumps, to be cleaned.
        s_noise is the signal of the recording of the surrounding noise.
        """
        
        self.s_noise = s_noise #attribut
        self.title = title
        
        self.s_length1, self.s_clean_bump1 = self.get_bump_length_and_clean(s_bump1)
        self.freqs_bump1 = self.get_strongest_freqs(self.s_clean_bump1, 5)
        self.s_length2, self.s_clean_bump2 = self.get_bump_length_and_clean(s_bump2)
        self.freqs_bump2 = self.get_strongest_freqs(self.s_clean_bump2, 5)
        self.s_length3, self.s_clean_bump3 = self.get_bump_length_and_clean(s_bump3)
        self.freqs_bump3 = self.get_strongest_freqs(self.s_clean_bump3, 5)

        verbose("s_length of " + str(self.title) + " : " + str(self.s_length), 3)
        a,b=self.s_bump.get_max()
        self.maxlevel_ord = a
        verbose("s_ordonate of " + str(self.title) + " : " + str(self.maxlevel_ord), 3)
        self.maxlevel_abs = b
        verbose("s_abscissa of " + str(self.title) + " : " + str(self.maxlevel_abs), 3) 
    
    def get_bump_length_and_clean(self, s_bump):
        max_noise = self.s_noise.get_max_level()
        threshold_noise=max_noise*c.START_TH_MULTIP
        verbose("threshold_noise : " + str(threshold_noise),3)
        
        i=0
        start=0
        while s_bump.data[i] < threshold_noise:
            if i==len(s_bump.data)-1:
                verbose("no bump detected",1)
                exit()
            i=i+1
        start=i 
        
        verbose("start:"+ str(start),3)
        
        i=len(s_bump.data)-1
        while s_bump.data[i] < threshold_noise:
            i-=1
        end=i
        
        verbose("end:"+ str(end),3)
        length = end-start
        
        clean_bump = s_bump.get_truncated(start, end+1)
        return length, clean_bump
        
    def get_strongest_freqs(self, s_clean_bump, n):
        """
        this function returns the frequencies whose intensities are the n greatest.
        
        On envoie au signal la liste des ordonnées du spectre, on abandonne ainsi l'abscisses (les ordonnées) pour un moment.
        On travaille donc avec des indices en abscisse. Une fois l'étude terminée, on récupère l'indice des piques, qu'on fait 
        correspondre aux fréquences avec la liste des abscisses de fréquences"""
        
        spec_freqs, spec_intensities = s_clean_bump.get_spectrum()        #get the spectrum of the clean bump
        signal = Signal("signal freqs", spec_intensities)                #create a signal from the intensities of the spectrum (we're thus considering the spectrum as supposed to be continuous, even though we know it's not)
        signal_2 = signal.get_derivated                                    #derivate this very signal
        list_abscissas = signal_2.get_symbol_change_abscissa()            #get the symbol changes, corresponding to abscissas of spikes 
        
        list_spikes_freqs = []                                            #now we have the abscissas of the spikes, in the scale of indices, we then have to "convert" them back so that we get the corresponding frequences
        for i in range(len(list_abscissas)):                            #this loop gets the corresponding frequencies
            list_spikes_freqs.append(spec_freqs[list_abscissas[i]])
        
        list_spikes_inten = []                                            
        for i in range(len(list_abscissas)):                            #this loop gets the intensities of the frequencies that correspond to a maximum
            list_spikes_inten.append(spec_intensities[list_abscissas[i]])
        
        #at this point of the program, list spikes freqs and list spikes inten contains the frequencies and intensities of the spikes
        #we now have to sort the lists so that we can get the n max out of these
        #we're using the selection sorting algorithm.
        
        list_n_max_inten = []    #list of ordered intensities
        list_n_max_freq = []    #list of the corresponding frequencies (not the maximum frequencies !)
        for j in range(len(list_spikes_inten)):
            max_inten = list_spikes_inten[0]
            for i in range(len(list_spikes_inten)):
                if list_spikes_inten[i] > max_inten:
                    max_inten = list_spikes_inten[i]
                    indice_max = i
            list_n_max_inten.append(max_inten)
            list_n_max_freq.append(list_spikes_freqs[indice_max])
            list_spikes_inten.pop(indice_max)
            list_spikes_freqs.pop(indice_max)
            
        return(list_n_max_freqs[0:n])
        
    # def list_freq_and_intensities_characteristics(self):
        # spec_freqs, spec_intensities = self.s_clean_bump.get_spectrum() # return 2 listes: self.spec_freqs, self.spec_intensities
        # max_spec_intensities = spec_intensities[0]
        # for i in range(len(spec_intensities)):
            # if spec_intensities[i] > max_spec_intensities:
                # max_spec_intensities = spec_intensities[i]
           
        # threshold_intensities = c.THRESHOLD_INTENSITIES_MULTIP * max_spec_intensities
        
        # verbose(" le seuil:" + str(threshold_intensities), 3)
        
        # i=0
        # spec_intensities_characteristics = []
        # spec_freqs_characteristics = []
        # for i in range(len(spec_intensities)):
            # if spec_intensities[i] > threshold_intensities:
                # spec_intensities_characteristics += [spec_intensities[i]]
                # spec_freqs_characteristics += [spec_freqs[i]]
        
        # verbose("liste des intensités cara:" + str(spec_intensities_characteristics), 3)
        # verbose("liste des fréqs cara:" + str(spec_freqs_characteristics), 3)
        
        # return spec_intensities_characteristics, spec_freqs_characteristics