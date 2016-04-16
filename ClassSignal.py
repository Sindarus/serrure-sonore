# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 20:02:26 2014

@author: Clément Saintier
"""

from scipy.io.wavfile import *          #This only works with "from _ import *"
import wave                             #This only works with "import _"

import scipy
import scipy.fftpack
import numpy as np
import pylab
import pyaudio                          #This only works with "import _"

from verbose import *
from ClassRecording import *

import config as c

class Signal:
    """This object depicts a signal, that means, it describes y = f(t) with t being time, y being intensity of the signal
    properties:
        - (str)     title :         title (=name) of the signal.
        - (int)     rate :          sampling rate
        - ([int])   data :          depicts the waveform of the signal
        - ([int])?  spec_freqs :    list of frequences that appear in the signal, after fft analysing
        - ([int])?  spec_intensities : intensities of the corresponding frequencies that appear in the signal, after fft analysing
    """
    
    def __init__(self, title, arg2):
        """
        Creates a signal with a title and from arg2 which can be either a Recording or a Data list, or a wav file
        
        title should be a STRING
        NB : the title of a signal can be different from the title of the recording it has been loaded from
        """
        
        self.rate = -1
        self.title = title
        self.spec_freqs = 0
        self.spec_intensities = 0
    
        if isinstance(arg2, Recording):
            verbose("loading signal '" + title + "' from assumed recording '" + arg2.title +  "' given",3)
            if arg2.recorded:
                self.data = arg2.data
                self.rate = arg2.rate
            else:
                verbose("error: provided recording '" + arg2.title + "' is empty", 1)
                quit()
        elif isinstance(arg2, list) or isinstance(arg2, numpy.ndarray):
            verbose("loading signal '" + title + "' from assumed data list given",3)
            self.data = arg2
        elif isinstance(arg2, str):
            verbose("loading signal '" + title + "' from assumed wav file given",3)
            self.rate, self.data = read(c.WORKING_DIR + arg2)
        else:
            verbose("Signal constructor called for '" + title + "' but no valid arg2 given ! It should be either a Recording or a Data list", 1)
            exit()
    
    def get_bt_threshold(self):
        """returns the list of times at which there's a bump, using threshold method
        
            This function analyses the signal, and detects bumps when the signal
            intensity goes above <threshold>.
            You can choose the way the threshold is set in config.py
            To prevent one bump to be analysed multiple times there's the following system :
            when the function detects a bump, it blocks itself for a certain amount of time, before being able to detect new bumps again
            you can set this amount of time in config.py
        """
        verbose("extracting bump times from " + self.title + " by threshold method",3)
        
        bumptimes = []
        lastbumptime = -9999
        threshold = -1
        
        #Setting threshold :
        if (c.THRESHOLD_AUTOSET == "maxlevel"):
            threshold = c.MAX_LEVEL_MULTIP * self.get_max_level()
            verbose("maxlevel is " + str(self.get_max_level()), 3)
            verbose("threshold is set by maxlevel to : " + str(threshold),3)
        elif (c.THRESHOLD_AUTOSET == "average"):
            threshold = c.AVERAGE_LEVEL_MULTIP * self.get_average_level()  
            verbose("threshold is set by average level to : " + str(threshold),3)
        elif (c.THRESHOLD_AUTOSET == "defined"):
            threshold = c.THRESHOLD_VALUE
            verbose("threshold was defined by you to : " + str(threshold),3)
        else:
            verbose("threshold setting method unknown", 1)
            exit()
            
        #Looking for bumps
        for i in range(1,len(self.data)):
            if (self.data[i] > threshold and
                    i-lastbumptime > c.MAX_BUMP_LENGTH):
                bumptimes.append(float(i) / 44100)
                lastbumptime = i
        
        #showing a graph with the signal + the threshold
        if(c.SHOW_WAVE):                                
            pylab.figure(1)
            pylab.plot(self.data, "r")
            if(c.SHOW_TH):
                pylab.plot([0,len(self.data)-1],[threshold, threshold],"blue")
            pylab.ylabel('level of signal ' + self.title)
            pylab.xlabel('time (1/44100 sec)')
            pylab.show()
        
        return bumptimes
    
    def show_wav(self):
        """Shows the waveform of the signal"""
        pylab.figure(1)
        pylab.plot(self.data,"r")
        pylab.ylabel('level of signal ' + self.title)
        pylab.xlabel('time (1/44100 sec)')
        pylab.show()
    
    def get_max(self):
        """Returns the coordinates (abscissa and ordinate) of the maximum of the positive part of the signal"""
        max_level = self.data[0]
        max_level_abs = 0
        for i in range(0,len(self.data)):
            if (self.data[i] > max_level):
                max_level = self.data[i]
                max_level_abs = i
        return max_level_abs, max_level
    
    def get_max_level(self):
        """Returns the maximum level of the positive part of the signal"""
        max_level = self.data[0]      
        for i in range(0,len(self.data)):
            if (self.data[i] > max_level):
                max_level = self.data[i]
        return max_level

    def get_positive_average(self):
        """returns the average level of the positive part of the signal"""
        sum = 0
        counter = 0
        for i in range(1,len(self.data)):
            if self.data[i]>0:
                sum += self.data[i]
                counter += 1
        average = float(sum)/counter
        return average
        
    def get_average(self, decimals = True):
        """
        returns the average level of the signal, positive and negative parts included
        
        NB : this is pretty useless: it should return almost 0 everytime
        """
        sum = 0
        for i in range(1,len(self.data)):
            sum += self.data[i]
        
        if decimals:
            average = float(sum)/len(self.data)
        else:
            average = sum/len(self.data)
            
        return average
    
    def get_bt_correlation(self, ref):
        """returns the list of times at which there's a bump, using correlation method
        
        ref is the signal of one isolated bump
        """
        start_times, averages = self.correlate_with(ref, c.CORRELATION_STEP)

        #je vais encore devoir abuser de la classe signal mtn...
        correlated = Signal("averages", averages)
        threshold = correlated.get_max_level()*0.2
        print("threshold =", str(threshold))
        #fin de l'abus
        
        bumptimes = []
        lastbumptime = -9999
        for i in range(1, len(averages)):
            if (averages[i] > threshold and start_times[i]-lastbumptime > c.MAX_BUMP_LENGTH):
                bumptimes.append(start_times[i]+len(ref)/2)
                lastbumptime = start_times[i]
        
        if(c.SHOW_WAVE):                                #showing a graph with the signal + the threshold
            pylab.figure(1)
            pylab.plot(start_times, averages, "r")
            if(c.SHOW_TH):
                pylab.plot([0,start_times[-1]],[threshold, threshold],"blue")
            pylab.ylabel('correlation function ' + self.title)
            pylab.xlabel('time (1/44100 sec)')
            pylab.show()
        
        return bumptimes
    
    def correlate_with(self, s2, step):
        """  |---------------------------------------------> passing time 
        s1:  +-+-+-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+ (analyzed signal)
        s2:         -+-+-+-+-+-+-+-+-                   (signal we're looking for)
        """

        if not isinstance(s2, Signal):
            verbose("searched signal given isn't a signal", 1)
            quit()
        
        averages = []
        start_times = []
        cur_start = 0
        while cur_start+len(s2) < len(self):
            cur_end = cur_start + len(s2)
            cur_s1 = self.get_truncated(cur_start,cur_end)
            cur_resul = cur_s1*s2
            averages.append(cur_resul.get_average(False))
            start_times.append(cur_start)
            cur_start += step
        
        if(c.CORRELATION_ABS):
            verbose("correlate_with : result of correlation was put in absolute value : result = abs(result)", 3)
            for i in range(len(averages)):
                averages[i] = abs(averages[i])
        
        return start_times, averages
    
    def get_data(self):
        """Returns the data of the wavefile
        
        This function returns the data in form of a list of Y coordinates
        representing the waveform. X coordinates of the waveform
        (corresponding to the time axis, Y being the intensity of the signal)
        can be deduced from the list index and the sampling rate, which is
        usually 44100Hz.
        """
        return self.data
    
    def get_truncated(self, start_time, end_time):
        """
        returns a signal composed by the signal being cut to start_time
        and end_time. End_time excluded.
        NB : start_time and end_time are number of samples, not seconds
        """
        if start_time>end_time:
            verbose("start time cannot be higher than end_time", 1)
            exit()
        return Signal(self.title + "_truncated", self.data[start_time:end_time])
        
    def calculate_spectrum(self):
        """analyses the signal to get its spectrum
        The FFT is ran from the WHOLE signal. if the signal is too long, it can give wierd results.
        
        NB: this should be used internally to this class. If you want to get the spectrum of this signal, use get_spectrum()
        """
        
        verbose("calculating spectrum of " + self.title, 3)
        
        t = []                            #creating timeline
        for i in range(len(self.data)):        #
            t.append(float(i/44100))      #the index of "data" is the number of samples, 2nd sample is equivalent to 2/44100 second       
        
        FFT = abs(scipy.fft(self.data))                                 #calculating the fft results
        freqs = scipy.fftpack.fftfreq(self.data.size, float(1/44100))   #calculating the frequencies that go along
    
        freqs = freqs[:len(freqs)/2]
        FFT = FFT[:len(FFT)/2]
    
        self.spec_freqs = freqs
        self.spec_intensities = FFT
    
    def get_spectrum(self):
        """returns two lists describing the graph of the frequential spectrum of the whole signal.
        
        first list is the list of frequences
        second list is the list of the intensity of each corresponding frequences
        """
        if not isinstance(self.spec_freqs, list):                #if the spectrum has never been calculated before,
            self.calculate_spectrum()           #calculate it !
        
        return self.spec_freqs, self.spec_intensities
    
    def get_strongest_freq(self):
        """returns the frequence that is the strongest in the signal
        
        _NB_ for some reason, the fft analysis gives wierd results sometimes,
        where the exact max frequency is not in the freqs list, and so, only
        the frequencies around the exact freq value have high intensities values.
        """
        if self.spec_freqs == 0:                #if the spectrum has never been calculated before,
            self.calculate_spectrum()           #calculate it !
        
        max_intensity = self.spec_intensities[0]
        max_intensity_freq = self.spec_freqs[0]
        for i in range(len(self.spec_freqs)):
            if self.spec_intensities[i] > max_intensity:
                max_intensity = self.spec_intensities[i]
                max_intensity_freq = self.spec_freqs[i]
        
        return max_intensity_freq
    
    def show_spectrum(self):
        """displays the spectrum of the self signal"""
        a,b = self.get_spectrum()
        pylab.figure(1)
        pylab.plot(a,b,"x")
        pylab.show()
    
    def get_enveloppe(self, n):
        """
        this function takes the maximum of the signal each n samples, and returns the maximums and abscissas
        03/06/2015 : this function is useless. What it does is useless ...
        """
        cur_debut = 0
        ordonnees = []
        abscisses = []
        while(cur_debut+n < len (self.data)):
            cur_max = self.data[cur_debut]
            cur_max_index = cur_debut
            for i in range(n):
                if self.data[cur_debut+i] > cur_max:
                    cur_max = self.data[cur_debut+i]
                    cur_max_index = cur_debut+i
                    
            ordonnees.append(cur_max)
            abscisses.append(cur_max_index)
            
            cur_debut+=n
        return abscisses, ordonnees
        
    def get_derivated(self):
        """Returns the derivate of the signal, using adjacent points method
        The derivate of the first point cannot be calculated with this method, and so, it'll take the value of the derivate of the next point
        and the derivate of the last point will be the derivate of the previous point
        """
        data_derivated = [0]
        for i in range(1,len(self.data)-1):
            data_derivated.append((self.data[i+1]-self.data[i-1]) / 2)
            
        data_derivated[0] = data_derivated[1]       #this is what we talked about in the docstrings
        data_derivated.append(data_derivated[-1])   #
        
        return Signal(self.title + "_derivated", data_derivated)
    
    def get_symbol_change_abscissa(self):
        """return
        """
        abscissa = []
        for i in range(len(self.data)-1):
            if self.data[i]*self.data[i+1] < 0:
                abscissa.append(i)
        
        return abscissa
        
    def __len__(self):
        return len(self.data)
    
    def __mul__(self, signal_mult):
        """THIS NEEDS DOCUMENTATION"""
        if not isinstance(signal_mult, Signal):
            verbose("you tried to multiply a signal with something that is not a signal", 1)
            exit()
        else:
            resultat = []
            if(len(self.data) != len(signal_mult.data)):
                verbose("signals aren't the same size, in mult_signal(data1, data2)", 1)
                verbose("first one is " + str(len(self.data)) + ", and the other is " + str(len(signal_mult.data)), 1)
                exit()
            else:
                for index, cur_value in enumerate(self.data):
                    resultat.append((self.data[index]/c.DIVISOR) * (signal_mult.data[index]/c.DIVISOR))
            s_resultat = Signal(self.title + "_x_" + signal_mult.title, resultat)
            return s_resultat
        
    def __repr__(self):
        self.show_wav()
        return "See the signal waveform of " + self.title
        