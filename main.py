# -*- coding: utf-8 -*-
"""
#########################
LINUX VERSION use on RPi
#########################

Created on Wed Dec 20 15:47:59 2017
@author: Rozsee
""" 
import obj
import funct
from funct import ACTION, modeVal, flags, stanceVal, walkVal 

########## VARIABLE DECLARATIONS ###########
#None

########## FUNCTION DEFINITIONS ###########
#None

########## PROGRAM START ########### 
kematox = obj.Hexapod("kematox")
funct.LookForDevices(kematox) 

while (True):
    try:
        funct.EventSource(funct.ds4)
        #print("MAIN: most kene mozogni...")
        funct.HxpdStateExecute(modeVal, flags, stanceVal, walkVal, kematox)
        
    except KeyboardInterrupt:
        funct.StopPrg(kematox)