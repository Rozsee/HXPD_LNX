# -*- coding: utf-8 -*-
"""
#########################
LINUX VERSION use on RPi
#########################

Created on Wed Dec 20 15:47:59 2017
@author: Rozsee
""" 
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import obj
import funct
import IK
import time
from copy import deepcopy
from IK import IK_in, IK_in_for_Swing, IK_Tripod_A, IK_Tripod_B, HeadMovInput, HeadCalibrVal, HeadMovOutput


""" VARIABLE DECLARATIONS """
modeVal = {"mode": 0, "prev_mode": 0 }
joyVal = {"PSBTN_counter": 0}
flags = {"position_reached": False, 
         "return_to_Ready": False, "return_to_Idle": False,
         "flag_thumbJoyStateChng_lx": False, "flag_thumbJoyStateChng_ly": False, 
         "flag_thumbJoyStateChng_rx": False, "flag_thumbJoyStateChng_ry": False,
         "flag_JoyStateChng_R2": False, "flag_shiftActivated": False, "flag_headModeSelected": False,
         "flag_DPAD_center": False, "flag_waswalking": False}
JoyBuffer = {"left_x": 0.0, "left_y": 0.0, "right_x": 0.0, "right_y": 0.0, "axis_R2": 0.0}
AxisBuffer ={
                "axis_lx": 0.0, "axis_ly": 0.0, "axis_rx": 0.0, "axis_ry": 0.0, "axis_L2": 0.0, "axis_R2":0.0,
                "prev_axis_lx": 0.0 , "prev_axis_ly": 0.0, "prev_axis_rx": 0.0, "prev_axis_ry": 0.0, "prev_axis_R2": 0.0,
                "lx_center": False, "ly_center": False, "rx_center": False, "ry_center": False, "R2_center": False
                
            }
auxVal = {"dist_to_grnd": 160.0, "lift_value": 35.0, "recoveryReq": False, "stanceVal": None}

walkVal = {"tripod_substep": 0, "walkmode": "TRIPOD", "tripod_step_1_complete": False, "tripod_step_2_complete": True, "POS_Z_old": 0.0}

EVENT = None


    
def JoyButtonHandler(event):
    """Mapping is according to the default driver. Connection trough bluetoothctl, no ds4drv installed
    joystick is recognised as 8 axes / 13 buttons, touchpad not implemented, gyro axes not implemented"""
    #print "DIAG: EVENT = JoyButtonHandler"
    for i in range(funct.ds4.get_numbuttons()):
        btn_ID = funct.ds4.get_button(i)                            
        if btn_ID == 1:                                                             # a button was pushed
            if i == 0: 
                event = "CROSS"
            elif i == 1: 
                event = "CIRCLE"
                EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal, HeadMovInput) # used to select head movement
            elif i == 2: 
                event = "TRIANGLE"                                                  # used for SHIFT
                EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal, HeadMovInput)                
            elif i == 3: 
                event = "SQUARE"
            elif i == 4: 
                event = "L1"
            elif i == 5: 
                event = "R1"
                #EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal)     # Not used
            elif i == 6: 
                event = "L2"
            elif i == 7: 
                event = "R2"
                #EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal)     # Not used
            elif i == 8: 
                event = "SHARE"
            elif i == 9: 
                event = "OPTIONS"                                                    # used for change operation modes
                EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal, HeadMovInput)
            elif i == 10: 
                event = "PSBTN"
                EventDispatch(event, modeVal, IK_in, AxisBuffer, flags, auxVal, HeadMovInput)      # used to return "READY" or "IDLE" operation mode
            elif i == 11: 
                event = "LEFT THUMB. BTN."
            elif i == 12: 
                event = "RIGHT THUMB. BTN."
            """
            elif i == 13: 
                event = "TOUCH SCREEN"                                              # Not implemented
            """
    
def ThumbJoyHandler(jbuff, axisbuff, flag_dict, event):
    axisbuff["axis_lx"] = funct.ds4.get_axis(0) * -1                                # Bal oldali thumbjoy az x és y tengel menti forgásokat adja
    if abs(axisbuff["axis_lx"]) < 0.1:
        if axisbuff["lx_center"] == False:
            axisbuff["axis_lx"] = 0
            jbuff["left_x"] = axisbuff["axis_lx"]
            axisbuff["lx_center"] = True
            flag_dict["flag_thumbJoyStateChng_lx"] = True
        elif axisbuff["lx_center"] == True:
            flag_dict["flag_thumbJoyStateChng_lx"] = False
    elif abs(axisbuff["axis_lx"]) > 0.1:
        if axisbuff["axis_lx"] != axisbuff["prev_axis_lx"]:
            axisbuff["prev_axis_lx"] = axisbuff["axis_lx"]
            jbuff["left_x"] = axisbuff["axis_lx"]
            axisbuff["lx_center"] = False
            flag_dict["flag_thumbJoyStateChng_lx"] = True
        else:
            flag_dict["flag_thumbJoyStateChng_lx"] = False
    
    axisbuff["axis_ly"] = funct.ds4.get_axis(1)
    if abs(axisbuff["axis_ly"]) < 0.1:
        if axisbuff["ly_center"] == False:
            axisbuff["axis_ly"] = 0
            jbuff["left_y"] = axisbuff["axis_ly"]
            axisbuff["ly_center"] = True
            flag_dict["flag_thumbJoyStateChng_ly"] = True
        elif axisbuff["ly_center"] == True:
            flag_dict["flag_thumbJoyStateChng_ly"] = False
    elif abs(axisbuff["axis_ly"]) > 0.1:
        if axisbuff["axis_ly"] != axisbuff["prev_axis_ly"]:
            axisbuff["prev_axis_ly"] = axisbuff["axis_ly"]
            jbuff["left_y"] = axisbuff["axis_ly"]
            axisbuff["ly_center"] = False
            flag_dict["flag_thumbJoyStateChng_ly"] = True
        else:
            flag_dict["flag_thumbJoyStateChng_ly"] = False

    axisbuff["axis_rx"] = funct.ds4.get_axis(3) * -1    
    if abs(axisbuff["axis_rx"]) < 0.1:
        if axisbuff["rx_center"] == False:
            axisbuff["axis_rx"] = 0
            jbuff["right_x"] = axisbuff["axis_rx"]
            axisbuff["rx_center"] = True
            flag_dict["flag_thumbJoyStateChng_rx"] = True
        elif axisbuff["rx_center"] == True:
            flag_dict["flag_thumbJoyStateChng_rx"] = False
    elif abs(axisbuff["axis_rx"]) > 0.1:
        if axisbuff["axis_rx"] != axisbuff["prev_axis_rx"]:
            axisbuff["prev_axis_rx"] = axisbuff["axis_rx"]
            jbuff["right_x"] = axisbuff["axis_rx"]
            axisbuff["rx_center"] = False
            flag_dict["flag_thumbJoyStateChng_rx"] = True
        else:
            flag_dict["flag_thumbJoyStateChng_rx"] = False

    axisbuff["axis_ry"] = funct.ds4.get_axis(4)
    if abs(axisbuff["axis_ry"]) < 0.1:
        if axisbuff["ry_center"] == False:
            axisbuff["axis_ry"] = 0
            jbuff["right_y"] = axisbuff["axis_ry"]
            axisbuff["ry_center"] = True
            flag_dict["flag_thumbJoyStateChng_ry"] = True
        elif axisbuff["ry_center"] == True:
            flag_dict["flag_thumbJoyStateChng_ry"] = False
    elif abs(axisbuff["axis_ry"]) > 0.1:
        if axisbuff["axis_ry"] != axisbuff["prev_axis_ry"]:
            axisbuff["prev_axis_ry"] = axisbuff["axis_ry"]
            jbuff["right_y"] = axisbuff["axis_ry"]
            axisbuff["ry_center"] = False
            flag_dict["flag_thumbJoyStateChng_ry"] = True
        else:
            flag_dict["flag_thumbJoyStateChng_ry"] = False
    
    
    axisbuff["axis_R2"] = funct.ds4.get_axis(5) + 1
    if axisbuff["axis_R2"] < 0.1:
        if axisbuff["R2_center"] == False:
            axisbuff["axis_R2"] = 0
            jbuff["axis_R2"] = axisbuff["axis_R2"]
            axisbuff["R2_center"] = True
            flag_dict["flag_JoyStateChng_R2"] = True
        elif axisbuff["R2_center"] == True:
            flag_dict["flag_JoyStateChng_R2"] = False
    elif axisbuff["axis_R2"] > 0.1:
        if axisbuff["axis_R2"] != axisbuff["prev_axis_R2"]:
            axisbuff["prev_axis_R2"] = axisbuff["axis_R2"]
            jbuff["axis_R2"] = axisbuff["axis_R2"]
            axisbuff["R2_center"] = False
            flag_dict["flag_JoyStateChng_R2"] = True
        else:
            flag_dict["flag_JoyStateChng_R2"] = False
    

    if flag_dict["flag_thumbJoyStateChng_lx"] or flag_dict["flag_thumbJoyStateChng_ly"] or flag_dict["flag_thumbJoyStateChng_rx"] or flag_dict["flag_thumbJoyStateChng_ry"] or flag_dict["flag_JoyStateChng_R2"] == True:
        event = "THMB_JOY"
        #print "THMB_JOYEVENT ---> THMB_JOYEVENT"
        EventDispatch(event, modeVal, IK_in, JoyBuffer, flags, auxVal, HeadMovInput)
        flag_dict["flag_thumbJoyStateChng"] = False
    
    
    
def EventSource():
    for event in funct.pygame.event.get():
        if event.type == funct.pygame.JOYBUTTONDOWN:
            JoyButtonHandler(EVENT)
            
        elif event.type == funct.pygame.JOYHATMOTION:           
            #funct.JoyHatHandler()
            hat_DIR = funct.ds4.get_hat(0)    
            if hat_DIR == (0,0):
                flags["flag_DPAD_center"] = True
            
            elif hat_DIR == (-1,0):                                               #LEFT                                        
                flags["flag_DPAD_center"] = False
                if auxVal["stanceVal"] == "default":
                    funct.DecresaeStance(kematox)
                    auxVal["stanceVal"] = "narrow"
                elif auxVal["stanceVal"] == "narrow":
                    print "MAIN: Lower stance limit reached"
                elif auxVal["stanceVal"] == "wide": 
                    funct.SetReadyPos(kematox, "set", auxVal)
                    auxVal["stanceVal"] = "default"

            elif hat_DIR == (1,0):                                              # RIGHT
                flags["flag_DPAD_center"] = False
                if auxVal["stanceVal"] == "default":
                    funct.IncreaseStance(kematox)
                    auxVal["stanceVal"] = "wide"
                elif auxVal["stanceVal"] == "narrow":
                    funct.SetReadyPos(kematox, "set", auxVal)
                    auxVal["stanceVal"] = "default"
                elif auxVal["stanceVal"] == "wide":
                     print "MAIN: Upper stance limit reached"
                     
            elif hat_DIR == (0,1):                                              # UP
                flags["flag_DPAD_center"] = False
                if modeVal["mode"] == 3:                                        # Ez a funkció csak mode =3-ban (WALK) működjön.
                    #set_POS_Z_for_Walk("UP", IK_in)
                    while flags["flag_DPAD_center"] == False:
                        
                        if IK.IK_in["POS_Z"] < 123.5:                           # Limited from calculated max value (130)
                            time.sleep(0.08)                                    # wait a bit
                            IK.IK_in["POS_Z"] =  IK.IK_in["POS_Z"] + 3.25       # do z tanslation up
                            print str(IK.IK_in["POS_Z"])
                            IK.IK_SixLeg()
                            kematox.MoveSixLeg(None, "support")
                            breakCond = funct.pygame.event.wait()
                            if breakCond.type == funct.pygame.JOYHATMOTION:
                                break
                            else:
                                continue
                        else:
                            IK.IK_in["POS_Z"] =  123.5
                            print "MAIN: POS_Z max. limit reached " + str(IK.IK_in["POS_Z"])     
                            break
                        
                else:
                    pass
                        
            elif hat_DIR == (0,-1):                                             # DOWN
                flags["flag_DPAD_center"] = False
                if modeVal["mode"] == 3:                                        # Ez a funkció csak mode =3-ban (WALK) működjön.
                    while flags["flag_DPAD_center"] == False:
                        
                        if IK.IK_in["POS_Z"] > 6.5:                             # Limited from calculated min value (0)
                            time.sleep(0.08)
                            IK.IK_in["POS_Z"] =  IK.IK_in["POS_Z"] - 3.25       # do z tanslation up
                            print str(IK.IK_in["POS_Z"])
                            IK.IK_SixLeg()
                            kematox.MoveSixLeg(None, "support")
                            breakCond = funct.pygame.event.wait()
                            if breakCond.type == funct.pygame.JOYHATMOTION:
                                break
                            else:
                                continue
                        else:
                            IK.IK_in["POS_Z"] =  6.5
                            print "MAIN: POS_Z min. limit reached " + str(IK.IK_in["POS_Z"])
                            break
                else:
                    pass
            
        elif event.type == funct.pygame.JOYAXISMOTION:
            #time.sleep(0.02) # szuresi kiserlet joymozgas was 0.15, was 0,1    # LINUS verzióbn a késleltetés szaggatottá teszi a mozgást ezért mellőzve
            ThumbJoyHandler(JoyBuffer, AxisBuffer, flags, EVENT)
    
    
def EventDispatch(event, mode_dict, direction_dict, jbuff, flag_dict, auxval, head_in):
    if (event == "OPTIONS"):                                                    # HA az OPTIONS gombot megnyomtak,
        print "MAIN: Changing mode..."
        mode_dict["prev_mode"] = mode_dict["mode"]
        if mode_dict["prev_mode"] == 3:
            flag_dict["return_to_Ready"] = True
            
        mode_dict["mode"] = mode_dict["mode"] + 1                               # akkor a mode valtozot noveljuk
        if mode_dict["mode"] == 4:                                              # HA mode = 4 (ilyen mode nincs), akkor
            print "MAIN: Returning to READY..."
            mode_dict["mode"] = 1                                               # menjunk vissza READY mode-ba
            
        event = ""                                                              # EVENT valtozo torlese
        print "MAIN: Mode is: " + str(mode_dict["mode"])
        flag_dict["position_reached"] = False
        
    elif (event == "PSBTN"):                                                    # HA a PS gombot 1x megnyomjuk, akkor visszatérünk ready-be,                
        if mode_dict["mode"] == 1:
            print "MAIN: Returning to IDLE..."
            mode_dict["mode"] = 0
            event = ""
            flag_dict["return_to_Ready"] = False
            flag_dict["return_to_Idle"] = True
            flag_dict["position_reached"] = False
            
        else:
            print "MAIN: Returning to READY..."
            mode_dict["mode"] = 1
            event = ""
            flag_dict["return_to_Ready"] = True
            flag_dict["return_to_Idle"] = False
            flag_dict["position_reached"] = False
         
    elif (event == "THMB_JOY"):
        if mode_dict["mode"] == 2:                                                                           # Thmb joy analog ertekeinek allokálása "STATIC" mod esetén (2)
            if flag_dict["flag_shiftActivated"] == False and flag_dict["flag_headModeSelected"] == False:    # HA SHIFT (Triangle button) nem aktív, akkor x, y tengely melntén forog, vagy "eltolodik" a robot
                direction_dict["ROT_X"] = 10 * jbuff["left_y"]                                               # ROT_X=BÓLINT ELŐRE
                direction_dict["ROT_Z"] = 20 * jbuff["left_x"]                                               # ROT_Z=CSAVAR FÜGGŐLEGES TENGELY KÖRÜL (was 10)
                direction_dict["POS_X"] = 50 * jbuff["right_x"]                                              # X=OLDALRA
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]                                              # Y=ELŐRE
                direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)
                flag_dict["position_reached"] = False
            elif flag_dict["flag_shiftActivated"] == True and flag_dict["flag_headModeSelected"] == False:   # HA SHIFT (Triangle button) aktív, akkor x,y mentén "eltolódik a robot, illetve Z tengely mentén fordúl
                direction_dict["POS_X"] = 50 * jbuff["right_x"] 
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]
                direction_dict["ROT_Y"] = 10 * jbuff["left_x"]                                               # ROT_Y=DÖL OLDLRA
                direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)
                flag_dict["position_reached"] = False
            elif flag_dict["flag_shiftActivated"] == False and flag_dict["flag_headModeSelected"] == True:
                direction_dict["POS_X"] = 50 * jbuff["right_x"] 
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]
                direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)

                head_in["headSide_diff"] = funct.calc_HeadSidePos(jbuff)                                     # uses jbuff["left_x"]
                head_in["headBow_diff"] = funct.calc_HeadBowPos(jbuff)                                       # uses jbuff["left_y"]

                flag_dict["position_reached"] = False
                
            elif flag_dict["flag_shiftActivated"] == True and flag_dict["flag_headModeSelected"] == True:
                direction_dict["POS_X"] = 50 * jbuff["right_x"] 
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]
                direction_dict["ROT_Y"] = 10 * jbuff["left_x"]                                               # ROT_Y=DÖL OLDLRA
                direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)

                head_in["headTwist_diff"] = funct.calc_HeadTwistPos(jbuff)

                flag_dict["position_reached"] = False
                    
        elif mode_dict["mode"] == 3:
            if flag_dict["flag_shiftActivated"] == False:  
                direction_dict["POS_X"] = 50 * jbuff["right_x"] 
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]
                direction_dict["ROT_Z"] = 20 * jbuff["left_x"]   
                #direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)                                   # This section is commented out. POS_Z is modified by D-PAD UP/DOWN instead of R2 button during WALK mode  
                flag_dict["position_reached"] = False
            elif flag_dict["flag_shiftActivated"] == True:  
                direction_dict["POS_X"] = 50 * jbuff["right_x"] 
                direction_dict["POS_Y"] = 50 * jbuff["right_y"]
                direction_dict["ROT_X"] = 10 * jbuff["left_y"]
                direction_dict["ROT_Y"] = 10 * jbuff["left_x"] 
                #direction_dict["POS_Z"] = funct.calc_POS_Z(IK_in, jbuff)                                   # This section is commented out. POS_Z is modified by D-PAD UP/DOWN instead of R2 button during WALK mode  
                flag_dict["position_reached"] = False

    elif (event == "TRIANGLE"):
        if mode_dict["mode"] == 2 or 3:
            if flag_dict["flag_shiftActivated"] == False:
                flag_dict["flag_shiftActivated"] = True
                print "MAIN: SHIFT is ON"
            elif flag_dict["flag_shiftActivated"] == True:
                flag_dict["flag_shiftActivated"] = False
                print "MAIN: SHIFT is OFF"

    elif (event == "CIRCLE"):
            if mode_dict["mode"] == 2 or 3:
                if flag_dict["flag_headModeSelected"] == False:
                    flag_dict["flag_headModeSelected"] = True
                    print "MAIN: Head mode is ON"
                elif flag_dict["flag_headModeSelected"] == True:
                    flag_dict["flag_headModeSelected"] = False
                    print "MAIN: Head mode is OFF"   

def EventExecute(event, mode_dict, flag_dict, auxval, walkval):
    if mode_dict["mode"] == 0: # IDLE
        if flag_dict["position_reached"] == False:
            if flag_dict["return_to_Idle"] == True:
                print "MAIN: Returning to IDLE"
                funct.SetIdlePos(kematox, "return")
                print "MAIN: IDLE position reached\n"
                flag_dict["return_to_Idle"] = False
                flag_dict["position_reached"] = True
            
            elif flag_dict["return_to_Idle"] == False:
                print "MAIN: MODE set to IDLE"                                  # ide még a fejet idle-be parancsot be kell szúrni
                funct.SetIdlePos(kematox, "set")
                print "MAIN: IDLE position reached\n"
                flag_dict["position_reached"] = True
                
        elif flag_dict["position_reached"] == True:
            pass
            
    elif mode_dict["mode"] == 1: # READY
        if flag_dict["position_reached"] == False:
            if flag_dict["return_to_Ready"] == True:
                print "MAIN: Returning to READY"
                funct.SetReadyPos(kematox, "return", auxVal)
                funct.CenterHead(kematox)
                print "MAIN: READY position reached\n"
                flag_dict["return_to_Ready"] = False
                flag_dict["position_reached"] = True
                
            elif flag_dict["return_to_Ready"] == False:
                print "MAIN: MODE set to READY"
                funct.SetReadyPos(kematox, "set", auxVal)
                funct.CenterHead(kematox)
                print "MAIN: READY position reached\n"
                flag_dict["position_reached"] = True
                
        elif flag_dict["position_reached"] == True:
            pass
            
    elif mode_dict["mode"] == 2: # STATIC
        if flag_dict["flag_headModeSelected"] == False:
            if flag_dict["position_reached"] == False:
                IK.IK_SixLeg()
                kematox.MoveSixLeg(None, "support")
                #IK.IK_Diag(IK.IK_out)
                flag_dict["position_reached"] = True
                print "DIAG: MOVEMENT READY"
            elif flag_dict["position_reached"] == True:
                pass
        elif flag_dict["flag_headModeSelected"] == True:
            if flag_dict["position_reached"] == False:
                IK.IK_SixLeg()
                kematox.MoveSixLeg(None, "support")
                IK.CalcHeadPos(HeadMovInput, HeadCalibrVal, HeadMovOutput)
                kematox.MoveHead(HeadMovOutput, 500)
                #IK.IK_Diag(IK.IK_out)
                flag_dict["position_reached"] = True
                print "DIAG: MOVEMENT READY"
            elif flag_dict["position_reached"] == True:
                pass
        
        
    elif mode_dict["mode"] == 3: # WALK
        time.sleep(0.05)
        WalkVector = IK.CalcWalkVector()
        #print "POS_X: " + str(IK.IK_in["POS_X"]) + "POS_Y: " + str(IK.IK_in["POS_Y"]) 
        #if ((abs(IK.IK_in["ROT_Z"]) > 0 and IK.IK_in["POS_Z"]) or (IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0)):
        if ((abs(IK.IK_in["ROT_Z"]) > 0 and IK.IK_in["POS_Z"]) or (WalkVector > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0)):
            #print "WALK"
            funct.TripodWalk(kematox, walkVal, "Walk")
            flag_dict["flag_waswalking"] = True
            
        elif (IK.IK_in["POS_Z"] > 0 or IK.IK_in["ROT_Y"] > 0 or WalkVector >0 or (IK.IK_in["ROT_Y"] > 0 and WalkVector >0) or (IK.IK_in["POS_Z"] == 0 and IK.IK_in["ROT_Y"] == 0 and WalkVector == 0)): 
            """Akkor is STATIC legyen a mód, ha minden 0 -> visszatérjen a robot alaphelyzetbe """
            #print "STATIC"
            
            if flag_dict["flag_waswalking"] == True:
                flag_dict["flag_waswalking"] = False
                funct.TripodWalk(kematox, walkVal, "Reset")
            
            if flag_dict["position_reached"] == False:
                IK.IK_SixLeg()
                kematox.MoveSixLeg(None, "support")
                flag_dict["position_reached"] = True
                print "DIAG: MOVEMENT READY"
            elif flag_dict["position_reached"] == True:
                pass

""" PROGRAM START """   
kematox = obj.Hexapod("kematox")
funct.InitDS4()
funct.LookForDevices(kematox) 

while (True):
    try:
        EventSource()
        EventExecute(EVENT, modeVal, flags, auxVal, walkVal)
        
    except KeyboardInterrupt:
        funct.StopPrg(kematox)