# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 20:02:26 2014

@author: Clément Saintier
"""

from scipy.io.wavfile import *          #This only works with "from _ import *"
import wave                             #This only works with "import _"

import numpy
import pylab
import pyaudio                          #This only works with "import _"

import config as c

from verbose import *

class Recording:
    """This object depicts a recording in its technical part.
    
    properties:
        - (str)     title :     title (=name) of the recording. it'll be the file's name
        - (str)     file_name : name of the associated .wav file, it is automatically set to title + ".wav"
        - (bool)    recorded :  tells whether the object is empty or loaded with data
        - (float)   duration :  duration of the recording (once data has been loaded, either by record(), or load_data()
        - (int)     rate :      sampling rate of the recording
        - ([int])   data :      depicts the waveform of the audio exctract, see scipy documentation for more info (or get_data() doc)
    """

    def __init__(self, title):
        """This constructor initializes a title and a duration for the instance
        of recording
        
        The title will be the file name (without .wav).
        after this, the object is still empty, and needs to be either recorded with record() or loaded with load_data() 
        """

        self.title = title
        self.file_name = c.WORKING_DIR + title + ".wav"
        self.duration = 0
        self.rate = 0
        self.data = 0
        
        #needed to know whether the recording has
        #already been done or not
        self.recorded = False   
    
    def record(self, duration):
        """Records <duration> second of audio
        
        This function records an audio extract of <self.duration> seconds,
        saves it under the name <self.title>.wav
        and loads data into the object
        """
        self.duration = duration
        
        verbose("duration of " + self.title + " : " + str(self.duration), 3)
        verbose("filename of " + self.title + " : " + str(self.file_name), 3)
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = self.duration
        WAVE_OUTPUT_FILENAME = self.file_name

        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        print("* recording " + self.title)
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("* done recording " + self.title)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        self.recorded = True
        self.load_data()
        
        self.data = self.data[c.CUT:]
        
    def show_wav(self):
        """Displays the wavform of the recording
        
        used for __repr__
        """
        x = []    
        
        for i in range(0,len(self.data)):
            x.append(i)

        pylab.plot(x, self.data,"r")
        pylab.show()
        
    def load_data(self):
        """Opens the .wav file linked to the Recording object, and loads its data into this object.
        
        This should be used internally to this class. If you want to work with a file that exists allready, use Signal("title", "name of file")
        NB: the wav file linked to the Recording object is named self.title followed by .wav
        """
        self.rate,self.data = read(self.file_name)
        self.duration = len(self.data)/self.rate
        self.recorded = True
        
        if (isinstance(self.data[0], numpy.ndarray)):
            verbose("Something obviously went wrong when loading " + self.title + ", because data[0] is an array. Check if the file that was loaded has only 1 channel.",1)
            quit()
    
    def get_data(self):
        """Returns the data of the wavefile
        
        This function returns the data in form of a list of Y coordinates
        representing the waveform. The X coordinates of the waveform
        (corresponding to the time axis, Y being the intensity of the signal)
        can be deduced from the list index and the sampling rate, which is
        usually 44100Hz.
        """
        return self.data
    
    def __repr__(self):
        """displays info about the recording
        
        NB: This method is called when you try to print() this object
        """
        if self.recorded:
            return "title of the Recording : " + self.title + " || duration : " + str(self.duration) + " || sampling rate : " + str(self.rate) + " samples per second"
        else:
            return "The recording " + self.title +" is empty"
    