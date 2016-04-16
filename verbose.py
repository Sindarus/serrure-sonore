# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 23:19:36 2014

@author: Clément Saintier
"""

import time
import datetime

import config as c

PRINT_MESSAGES = True
LOG_MESSAGES = True
VERBOSE_LEVEL_PRINT = 2
VERBOSE_LEVEL_LOG = 2
#1-only show fataly important messages (the ones that require exiting the programm)
#2-show less important messages as well (still important but no need to exit the programm)
#3-show trivial messages concerning the normal functionning of the progamm as well

def verbose(message, level = -1):
    """
    this function writes message in log.txt and/or displays them on screen, depending on configuration
    
    messages of ALL level will be recorded 
    """
    
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M:%S')
    
    if level == -1:
        verbose("The level of this verbose message has not been set, or set to -1. Assuming level 1.", 2)
        level = 1
    
    if PRINT_MESSAGES:
        if level <= VERBOSE_LEVEL_PRINT:
            print("[" + str(level) + "] " + str(message))
    
    if LOG_MESSAGES:
        if level <= VERBOSE_LEVEL_LOG:
            log = open(c.WORKING_DIR + "log.txt", "a")
            log.write(date + " : [" + str(level) + "] " + str(message) + "\n")
            log.close()