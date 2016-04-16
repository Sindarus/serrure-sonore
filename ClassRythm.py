# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 20:02:26 2014

@author: Clément Saintier
"""

from verbose import *

import config as c

class Rythm:
    def __init__(self, title, signal, ref = 0):
        """
        creates a Rythm with a title, from a Signal given. ref is the signal of an isolated bump, if method used is correlate.
        
        This constructor handles analysing the signal given, to extract the rythm from it
        title should be a STRING
        """
        
        self.title = title
        self.rythm = 0
        self.bumptimes = []
        
        if c.METHOD == "threshold" :
            verbose("extracting rythm " + title + "from " + signal.title + " signal, by threshold method", 3)
            self.bumptimes = signal.get_bt_threshold()
        elif c.METHOD == "correlation" :
            verbose("extracting rythm " + title + "from " + signal.title + " signal, by correlation method", 3)
            self.bumptimes = signal.get_bt_correlation(ref)
        
        if c.SHOW_BT:
            print("exctracted bt are : " + self.repr_bt())
        
        self.bt_to_rythm()
    
    def bt_to_rythm(self):
        """
        this function updates self.rythm for a list of bumptimes given
        rythm means that the first term will be 0 and the last will be 1000
        """
        
        verbose("converting given bumptimes into a rythm '" + self.title + "'",3)
        verbose("bumptimes : " + self.show_bt(), 3)
        times = list(self.bumptimes)        #so that bump_times isn't modified ... we never know, with python ...
        #also, list() is needed to clone a list. Otherwise, it'd just make a pointer to self.bumtimesor something like that
        
        if (len(times) > 2):
            gap = times[0]                #making the first bumptime 0, and
            for i in range(0,len(times)):           #delaying other values
                times[i] = times[i]-gap
                
            ratio = 1000/float(times[-1])
            for i in range(0,len(times)):
                times[i] = times[i]*ratio
                
            self.rythm = times
        else:
            verbose("can't make a rythm out of these bumptimes : ", 2)
            verbose(str(times), 2)
            verbose("continuing... assuming [0,1000]", 2)
            self.rythm = [0,1000]
        
        verbose("rythm : " + self.__repr__(), 3)
            
    def show_bt(self):
        s = "["
        for i in self.bumptimes:
            s += str(round(i, 2)) + ", "
        s = s[0:len(s)-2]
        s+= "]"
        return s
    
    def __eq__(self, other):
        '''other is supposed to be the key rythm'''
        if not isinstance(other, Rythm):
            return 0
    
        if(c.KEY_METHOD == "simple"):
            if (len(self.rythm) != len(other.rythm)):     #if the given rythm contains less bumps than the key, we know it's false
                verbose("rythms " + self.title + " and " + other.title + " haven't got the same length, they can't be equal", 3)
                return 0
                
            for i in range(len(self.rythm)):
                if not (other.rythm[i]-c.TOLERANCE <= self.rythm[i] and self.rythm[i] <= other.rythm[i]+c.TOLERANCE):
                    return 0
            return 1
            
        elif(c.KEY_METHOD == "complex"):
            if (len(self.bumptimes) != len(other.bumptimes)):     #if the given rythm contains less bumps than the key, we know it's false
                verbose("bumptimes from rythms " + self.title + " and " + other.title + " haven't got the same length, they can't be equal", 3)
                return 0
            
            #number of hit in the rythm
            n = len(self.bumptimes)
            
            #sum of times in the tested rythm:
            #sum of times in the tested rythm, squared
            #sum of ai*ri
            #sum of ri
            sum_ai = 0
            sum_ai_squared = 0
            sum_ai_ri = 0
            sum_ri = 0
            for i,j in enumerate(self.bumptimes):
                sum_ai += j
                sum_ai_squared += j**2
                sum_ai_ri += self.bumptimes[i] * other.bumptimes[i]
                sum_ri += other.bumptimes[i]
                
            # print("sum_ai = " + str(sum_ai))
            # print("sum_ai_squared = " + str(sum_ai_squared))
            # print("sum_ai_ri = " + str(sum_ai_ri))
            # print("sum_ri = " + str(sum_ri))
                
            #expension factor
            B = (sum_ai_ri - ((sum_ai*sum_ri)/n) ) / (sum_ai_squared - ((sum_ai**2)/n))
            print("B = " + str(B))
            
            #interval factor
            A = (sum_ri - sum_ai * B) / n
            print("A = " + str(A))
            
            #determine gap between tested rythm and key :
            gap = 0
            for i in range(len(self.bumptimes)):
                gap += ( (A + B*self.bumptimes[i]) - other.bumptimes[i] )**2
            
            verbose("detected gap between" + self.title + " and " + other.title + " is " + str(gap), 3)
            
            if c.SHOW_GAP:
                print("gap is : " + str(gap))
                
            if c.LOG_GAPS:
                verbose("gap is : " + str(gap), 1)
            
            #do we accept this gap ?
            if gap <= c.MAX_GAP:
                return 1
            else:
                return 0
            
        else:
            verbose("in rythm.eq() key_method unknown",1)
            quit()
    
    def repr_bt(self):
        if self.bumptimes == []:
            return str("no bumptimes defined for this rythm")
        else:
            s = "["
            for i in self.bumptimes:
                s += str(round(i,2)) + ", "
            s = s[0:len(s)-2]
            s += "] x"
            s += str(len(self.bumptimes))
            return s
    
    def __repr__(self):
        if self.rythm == 0:
            return str("this rythm is not defined")
        else:
            s = "["
            for i in self.rythm:
                s += str(int(i)) + ", "
            s = s[0:len(s)-2]
            s += "] x"
            s += str(len(self.rythm))
            return s