# -*- coding: utf-8 -*-
"""
#########################
LINUX VERSION use on RPi
#########################

Created on Fri Jan 26 21:27:17 2018
@author: Rozsee
"""
########## IMPORTS ###########
import time
import sys
import IK
import obj
from IK import HeadMovInput, HeadCalibrVal, HeadMovOutput, IK_in, IK_Tripod_A, IK_Tripod_B
from evdev import InputDevice, categorize, ecodes
#from main import kematox                                                       # erre itt nincs szükség. Majd  a Main()-ban a HxpdStateExecute()-nak átadjuk a kematox objektumot


########## VARIABLE DECLARATIONS ###########
global CmdBuf
CmdBuf = ""                                                                     # globális válozo deklarása. Így kell, 2 sor...
ACTION = None                                                                   # variable to save event type to use in HxpdStateSet()
AxisBuffer ={
                "axis_lx": 0.0, "axis_ly": 0.0, "axis_rx": 0.0, "axis_ry": 0.0, "axis_L2": 0.0, "axis_R2":0.0,
                "prev_axis_lx": 0.0 , "prev_axis_ly": 0.0, "prev_axis_rx": 0.0, "prev_axis_ry": 0.0, "prev_axis_R2": 0.0,
                "lx_center": False, "ly_center": False, "rx_center": False, "ry_center": False, "R2_center": False
            }
JoyBuffer = {"left_x": 0.0, "left_y": 0.0, "right_x": 0.0, "right_y": 0.0, "axis_R2": 0.0}
flags = {"position_reached": False, 
         "return_to_Ready": False, "return_to_Idle": False,
         "flag_thumbJoyStateChng_lx": False, "flag_thumbJoyStateChng_ly": False, 
         "flag_thumbJoyStateChng_rx": False, "flag_thumbJoyStateChng_ry": False,
         "flag_JoyStateChng_R2": False, "flag_shiftActivated": False, "flag_headModeSelected": False,
         "flag_DPAD_center": False, "flag_DPAD_left": False, "flag_DPAD_right": False, "flag_DPAD_up": False, "flag_DPAD_down": False,
         "flag_waswalking": False, "flag_EmergencyStop": False, "flag_freeze_POS_Z": False}
modeVal = {"mode": 0, "prev_mode": 0, "EmgModeLvl": 0 }
stanceVal = {"stance": "default", "setTo": None}
walkVal = {"tripod_substep": 0, "walkmode": "TRIPOD", "tripod_step_1_complete": False, "tripod_step_2_complete": True, "POS_Z_old": 0.0}

""" JOYSTICK BUTTON CODES (EVDEV) """
CROSS = 304
SQUARE = 308
TRIANGLE = 307
CIRCLE = 305
PS = 316
SHARE = 314
OPTIONS = 315
R1 = 311
L1 = 310
R2 = 313
L2 = 312
R_JOY_BTN = 318
L_JOY_BTN = 317


########### FUNCTION DEFINITIONS ############
# """ INIT FUNCTIONS FOR PHERIPHERIALS... """
# StopPrg()
# LookForDevices()

def StopPrg(robot):
    """ 
        function:
            Stops program. Closes / releases serial port that was used by SSC32 servo controller and exits.
        parameters:
            robot = An instance of the class Heapod -> The robot itself (kematox)
        returns:
            None        
    """
    ReleaseAllServos(robot)
    print("FUNCT.: Servos released...")
    robot.SRVCTRL.Port.close()
    print ("FUNCT.: Serial port released...")
    print ("FUNCT.: Exiting...")
    sys.exit(0)

def LookForDevices(robot):
    """function:
            Checks if pheripherials are avaliable and connection is possible to them. Also provides basic info about them.
        parameters: 
            robot = An instance of the class Heapod -> The robot itself (kematox)
        returns:
            None
    """
    # Joystick
    global ds4
    ds4 = InputDevice('/dev/input/event3')                                          # Controller init
    print("FUNCT: Controller: " + str(ds4))
    print ("FUNCT.: Controller name: " + str(ds4.name))
    print ("FUNCT.: Controller address: " + str(ds4.uniq))

    # Servo Controller SSC32
    robot.SRVCTRL.Port.write("VER\r\n".encode())
    version = robot.SRVCTRL.Port.readline()
    robot.SRVCTRL.Port.write("Q\r\n".encode())
    resp_raw = robot.SRVCTRL.Port.readline()
    resp = resp_raw.decode()
    if resp == '.':
        print ("FUNCT.: SSC32-Servo controller found. Firmware version: " + version.decode())
        print ("FUNCT.: Ready\n")
    else:
        print ("FUNCT.: Servo controller not found, exiting...")
        StopPrg(robot)
    
    # ADCPI
    # PhidGet Motion Sensor

# """ JOYSTICK RELATED DEFINITIONS """
# JoyButtonHandler()
# JoyDPadHandler()
# JoyThumbJoyHandler()

def JoyButtonHandler(event, action):
    """ function: 
            decodes button codes and sets the action variable according to it
        parameters:
            event = Event that comes from polling the controller and trasferred from EventSource()
            action = variable transferred from EventSource() and the type of action will be saved in it to process by HxpdStateSet()
    """
    if event.value == 1:
      if event.code == CROSS:
        action = "CROSS"
      elif event.code == SQUARE:
        action = "SQUARE"
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == TRIANGLE:
        action = "TRIANGLE"
        #print("TRIANGLE BTN")
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == CIRCLE:
        action = "CIRCLE"
        #print("CIRCLE BTN")
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == PS:
        action = "EMERGENCY_STOP"
        #print("PS BTN")
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == SHARE:
        action = "SHARE"
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == OPTIONS:
        action = "OPTIONS"
        #print("OPTIONS BTN")
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
      elif event.code == R1:
        action = "R1"
      elif event.code == L1:
        action = "L1"
      elif event.code == R2:
        action = "R2"
      elif event.code == L2:
        action = "L2"
      elif event.code == L_JOY_BTN:
        action = "LEFT_JOY_BUTTON"
      elif event.code == R_JOY_BTN:
        action = "RIGHT_JOY_BTN"

def JoyDPadHandler(event, flgs, action):
    """ function:
            decodes the DPAD (Direction Pad) button codes and sets the action variable according to it
        parameters:
            event = Event that comes from polling the controller and trasferred from EventSource()
            action = variable transferred from EventSource() and the type of action will be saved in it to process by HxpdStateSet()
    """
    if event.code == ecodes.ABS_HAT0X:
        print("HAT_X EVENT")
        if event.value == -1:                                   # DPAD-LEFT direction
            action = "DPAD_LEFT"
            HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
        elif event.value == 1:                                  # DPAD-RIGHT dirction
            action = "DPAD_RIGHT"
            HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
    
    elif event.code == ecodes.ABS_HAT0Y:
        print("HAT_Y EVENT")
        if event.value == -1:                                   # DPAD-DOWN direction
            flgs["flag_DPAD_center"] = False
            action = "DPAD_DOWN"
            HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
        elif event.value == 1:                                  # DPAD-UP direction
            flgs["flag_DPAD_center"] = False
            action = "DPAD_UP"
            HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)

def JoyThumbJoyHandler(event, action, axisbuff, jbuff, flgs):
    """ function:
            gets the axis value, rescales it, decide if there is a change compared to the previous value and transfers value to joysticbuffer
        parameters:
            event = Event that comes from polling the controller and trasferred from EventSource()
            action = variable transferred from EventSource() and the type of action will be saved in it to process by HxpdStateSet()
            axis_buff = points to the temporary storage of rescaled axis values
            jbuff = points to the main storage of rescaled axis values. These variable will be as an input used in IK calculation
            flgs = points to the general boolean status indicating variable container
    """
    def RescaleAxisRawVal(event):
        """ function: 
                rescales the axis reading to [-1,1] interval
            parameters: 
                event = that comes from polling the controller and trasferred from EventSource()
            returns:
                rescaledAxisVal = rescaled axis reading with filtering
        """
        rescaledAxisVal = ((event.value / 130) -1)
        #print("****RESCALED_VAL = " + str(rescaledAxisVal) + "****")
        if abs(rescaledAxisVal) < 0.15:
            rescaledAxisVal = 0
        return rescaledAxisVal
    
    if event.code == ecodes.ABS_X:                              # LEFT JOY. X VALUE
        #print("JOY LX_EVENT")
        axisbuff["axis_lx"] = RescaleAxisRawVal(event)
        if axisbuff["axis_lx"] == 0:
            if axisbuff["lx_center"] == False:
                jbuff["left_x"] = axisbuff["axis_lx"]
                axisbuff["lx_center"] = True
                flgs["flag_thumbJoyStateChng_lx"] = True
            elif axisbuff["lx_center"] == True:
                flgs["flag_thumbJoyStateChng_lx"] = False
        #elif axisbuff["axis_lx"] > 0.1:
        else:
            if axisbuff["axis_lx"] != axisbuff["prev_axis_lx"]:
                axisbuff["prev_axis_lx"] = axisbuff["axis_lx"]
                jbuff["left_x"] = axisbuff["axis_lx"]
                axisbuff["lx_center"] = False
                flgs["flag_thumbJoyStateChng_lx"] = True
            else:
                flgs["flag_thumbJoyStateChng_lx"] = False

    elif event.code == ecodes.ABS_Y:                            # LEFT JOY. Y VALUE
        #print("JOY LY_EVENT")
        axisbuff["axis_ly"] = RescaleAxisRawVal(event)
        if axisbuff["axis_ly"] == 0:
            if axisbuff["ly_center"] == False:
                jbuff["left_y"] = axisbuff["axis_ly"]
                axisbuff["ly_center"] = True
                flgs["flag_thumbJoyStateChng_ly"] = True
            elif axisbuff["ly_center"] == True:
                flgs["flag_thumbJoyStateChng_ly"] = False
        #elif axisbuff["axis_ly"] > 0.1:
        else:
            if axisbuff["axis_ly"] != axisbuff["prev_axis_ly"]:
                axisbuff["prev_axis_ly"] = axisbuff["axis_ly"]
                jbuff["left_y"] = axisbuff["axis_ly"]
                axisbuff["ly_center"] = False
                flgs["flag_thumbJoyStateChng_ly"] = True
            else:
                flgs["flag_thumbJoyStateChng_ly"] = False

    elif event.code == ecodes.ABS_RX:                           # RIGHT JOY. X VALUE
        #print("JOY RX_EVENT")
        axisbuff["axis_rx"] = RescaleAxisRawVal(event)
        if axisbuff["axis_rx"] == 0:
            if axisbuff["rx_center"] == False:
                jbuff["right_x"] = axisbuff["axis_rx"]
                axisbuff["rx_center"] = True
                flgs["flag_thumbJoyStateChng_rx"] = True
            elif axisbuff["rx_center"] == True:
                flgs["flag_thumbJoyStateChng_rx"] = False
        #elif axisbuff["axis_rx"] > 0.1:
        else:
            if axisbuff["axis_rx"] != axisbuff["prev_axis_rx"]:
                axisbuff["prev_axis_rx"] = axisbuff["axis_rx"]
                jbuff["right_x"] = axisbuff["axis_rx"]
                axisbuff["rx_center"] = False
                flgs["flag_thumbJoyStateChng_rx"] = True
            else:
                flgs["flag_thumbJoyStateChng_rx"] = False

    elif event.code == ecodes.ABS_RY:                           # RIGHT JOY. Y VALUE
        #print("JOY RY_EVENT")
        axisbuff["axis_ry"] = RescaleAxisRawVal(event)
        if axisbuff["axis_ry"] == 0:
            if axisbuff["ry_center"] == False:
                jbuff["right_y"] = axisbuff["axis_ry"]
                axisbuff["ry_center"] = True
                flgs["flag_thumbJoyStateChng_ry"] = True
            elif axisbuff["ry_center"] == True:
                flgs["flag_thumbJoyStateChng_ry"] = False
        #elif axisbuff["axis_ry"] > 0.1:
        else:
            if axisbuff["axis_ry"] != axisbuff["prev_axis_ry"]:
                axisbuff["prev_axis_ry"] = axisbuff["axis_ry"]
                jbuff["right_y"] = axisbuff["axis_ry"]
                axisbuff["ry_center"] = False
                flgs["flag_thumbJoyStateChng_ry"] = True
            else:
                flgs["flag_thumbJoyStateChng_ry"] = False

    elif event.code == ecodes.ABS_RZ:                           # R2 BUTTON ANALOG VALUE (for static Z axis translation)
        axisbuff["axis_R2"] = event.value / 255
        if axisbuff["axis_R2"] < 0.1:
            if axisbuff["R2_center"] == False:
                axisbuff["axis_R2"] = 0
                jbuff["axis_R2"] = axisbuff["axis_R2"]
                axisbuff["R2_center"] = True
                flgs["flag_JoyStateChng_R2"] = True
            elif axisbuff["R2_center"] == True:
                flgs["flag_JoyStateChng_R2"] = False
        elif axisbuff["axis_R2"] > 0.1:
            if axisbuff["axis_R2"] != axisbuff["prev_axis_R2"]:
                axisbuff["prev_axis_R2"] = axisbuff["axis_R2"]
                jbuff["axis_R2"] = axisbuff["axis_R2"]
                axisbuff["R2_center"] = False
                flgs["flag_JoyStateChng_R2"] = True
            else:
                flgs["flag_JoyStateChng_R2"] = False

    if flgs["flag_thumbJoyStateChng_lx"] or flgs["flag_thumbJoyStateChng_ly"] or flgs["flag_thumbJoyStateChng_rx"] or flgs["flag_thumbJoyStateChng_ry"] or flgs["flag_JoyStateChng_R2"] == True:
        action = "THMB_JOY"
        HxpdStateSet(action, modeVal, IK_in, JoyBuffer, flags, HeadMovInput, stanceVal, ds4)
        flgs["flag_thumbJoyStateChng"] = False

# """ MAIN PROGRAM EVENT HANDLER DEFINITIONS """
# EventSource()
# HxpdStateSet()
# HxpdStateExecute()

def EventSource(controller):
    """ function:
            identifies the triggers coming from any source (now joystick) and calls the corresponding definitoon to decode them
        parameters:
            controller = joystick object defined at InitDS4
        returns: None
    """
    #print ("Executing Eventsource()")
    for event in controller.read_loop():
        #print("forban pörög...")
        if event.type == ecodes.EV_KEY:
            JoyButtonHandler(event, ACTION)
            break

        elif event.type == ecodes.EV_ABS:
            if event.code == (ecodes.ABS_HAT0X):
                JoyDPadHandler(event, flags, ACTION)
                break
            
            elif event.code == (ecodes.ABS_HAT0Y):
                JoyDPadHandler(event, flags, ACTION)
                break

            elif event.code == (ecodes.ABS_X):
                JoyThumbJoyHandler(event, ACTION, AxisBuffer, JoyBuffer, flags)
                break

            elif event.code == (ecodes.ABS_Y):
                JoyThumbJoyHandler(event, ACTION, AxisBuffer, JoyBuffer, flags)
                break

            elif event.code == (ecodes.ABS_RX):
                JoyThumbJoyHandler(event, ACTION, AxisBuffer, JoyBuffer, flags)
                break

            elif event.code == (ecodes.ABS_RY):
                JoyThumbJoyHandler(event, ACTION, AxisBuffer, JoyBuffer, flags)
                break

            elif event.code == (ecodes.ABS_RZ):
                JoyThumbJoyHandler(event, ACTION, AxisBuffer, JoyBuffer, flags)
                break



def HxpdStateSet(action, mode, directions, jbuff, flgs, head_in, stance, controller):
    """function:
            Set the desired state of the robot according to the input triggers.
        parameters:
            action = variable transferred from EventSource() and the type of action will be saved in it to process by HxpdStateSet()
            mode = points to a variable containing the actual / desired opMode of the robot
            directions = dictonary containing POS_XYZ and ROT_XYZ values for IK calculation for robot BODY
            jbuff = points to the main storage of rescaled axis values. These variable will be as an input used in IK calculation
            flgs = points to the general "boolean status indicating" variable container
            head_in = dictonary containing POS_XYZ and ROT_XYZ values for IK calculatio for robot HEAD
            stance = points to a variable containing the actual / desired value of robot stance
            controller = 
        returns: 
            None
    """
    def DPADReleased(controller):
        """function:
                Checks if DPAD button was released
            parameters:
                controller = joystick object / instance to poll for catching DPAD button release
            returns:
                exitCond = Boolean variable. If True DPAD button was released
        """
        exitCond = None
        for exit in controller.read_loop():
            if (exit.type == ecodes.EV_ABS and exit.code == ecodes.ABS_HAT0Y and exit.value == 0):
                exitCond = True
                return exitCond
            else:
                exitCond = False
                return exitCond

    def calc_POS_Z(directions, jbuff):
        """function:
                Calculates POS_Z, based on the analog readings of DS4 controller R2 button / axis
            parameters:
                directions = dictonary containing POS_XYZ and ROT_XYZ values for IK calculation for robot BODY
                jbuff = points to the main storage of rescaled axis values. These variable will be as an input used in IK calculation
            returns:
                pos_z = calculated POS_Z valu that can be used during IK calculation
        """
        ZminVal = directions["z"]
        ZmaxVal = 240
        minRawaxisVal = 0
        maxRawaxisVal = 1
        
        pos_z = ((((ZmaxVal - ZminVal) / (maxRawaxisVal - minRawaxisVal)) * jbuff["axis_R2"]) + ZminVal) - ZminVal
        return pos_z
    
    #print ("Executing HxpdStateSet()")
    #print("Action is:" + action)
    
    if action == "CIRCLE":                                  # TOGGLE HEAD FUNCTIONS 
        if mode["mode"] == 2 or 3:
            if flgs["flag_headModeSelected"] == False:
                flgs["flag_headModeSelected"] = True
                print ("FUNCT.: Head mode is ON")
                action = None
            elif flgs["flag_headModeSelected"] == True:
                flgs["flag_headModeSelected"] = False
                print ("FUNCT.: Head mode is OFF")
                action = None

    elif action == "TRIANGLE":                              # SHIFT FUNCTION TOGGLE
        if mode["mode"] == 2 or 3:
            if flgs["flag_shiftActivated"] == False:
                flgs["flag_shiftActivated"] = True
                print ("FUNCT.: SHIFT is ON")
                action = None
            elif flgs["flag_shiftActivated"] == True:
                flgs["flag_shiftActivated"] = False
                print ("FUNCT.: SHIFT is OFF")
                action = None

    elif action == "OPTIONS":                               # TOGGLE OPMODE
        print ("FUNCT.: Changing mode...")   
        mode["prev_mode"] = mode["mode"]
        mode["mode"] = mode["mode"] + 1                                     # a mode valtozot noveljuk
        if mode["mode"] == 4:                                               # HA mode = 4 (ilyen mode nincs), akkor
            print ("FUNCT.: Returning to READY...")
            mode["mode"] = 1                                                # menjunk vissza READY mode-ba
        elif mode["mode"] == 11:                                            # Ha Emergency mode-ban vagyunk, ne lehessen tovább növelni a mode változót,
            mode["mode"] = 10                                               #az mindíg maradjon 10
            
        if mode["prev_mode"] == 3:
            flgs["return_to_Ready"] = True

        action = None                                                         # EVENT valtozo torlese
        print ("FUNCT.: Mode is: " + str(mode["mode"]))
        flgs["position_reached"] = False

    elif action == "SHARE":                                 # RETURN TO READY OR IDLE MODE
        if mode["mode"] == 1:
            print ("FUNCT.: Returning to IDLE...")
            mode["mode"] = 0
            flgs["return_to_Ready"] = False
            flgs["return_to_Idle"] = True
            flgs["position_reached"] = False
            action = None

        else:
            print ("MAIN: Returning to READY...")
            mode["mode"] = 1
            flgs["return_to_Ready"] = True
            flgs["return_to_Idle"] = False
            flgs["position_reached"] = False
            action = None

    elif action == "DPAD_LEFT":                             # INITIATE NARROW STANCE
        if mode["mode"] == 2:
            if stance["stance"] == "default":
                stance["setTo"] = "narrow"
                flgs["position_reached"] = False
                action = None
            elif stance["stance"] == "narrow":
                print ("FUNCT.: Lower stance limit reached")
                action = None
            elif stance["stance"] == "wide": 
                stance["setTo"] = "narrow"
                flgs["position_reached"] = False
                action = None

    elif action == "DPAD_RIGHT":                            # INITIATE WIDE STANCE
        if mode["mode"] == 2:
            if stance["stance"] == "default":
                stance["setTo"] = "wide"
                flgs["position_reached"] = False
                action = None
            elif stance["stance"] == "wide":
                print ("FUNCT.: Upper stance limit reached")
                action = None
            elif stance["stance"] == "narrow":
                stance["setTo"] = "wide"
                flgs["position_reached"] = False
                action = None
        
    elif action == "DPAD_UP":                               # Pass action execution to HxpdStateExecute()
        flgs["flag_DPAD_up"] = True
        action = None
    elif action == "DPAD_DOWN":
        flgs["flag_DPAD_down"] = True
        action = None

    elif action == "THMB_JOY":
        if mode["mode"] == 2:                                                                            # Thmb joy analog ertekeinek allokálása "STATIC" mod esetén (2)
            if flgs["flag_shiftActivated"] == False and flgs["flag_headModeSelected"] == False:          # HA SHIFT (Triangle button) nem aktív, akkor x, y tengely melntén forog, vagy "eltolodik" a robot
                directions["ROT_X"] = 10 * jbuff["left_y"]                                               # ROT_X=BÓLINT ELŐRE
                directions["ROT_Z"] = 20 * jbuff["left_x"]                                               # ROT_Z=CSAVAR FÜGGŐLEGES TENGELY KÖRÜL (was 10)
                directions["POS_X"] = 50 * jbuff["right_x"]                                              # X=OLDALRA
                directions["POS_Y"] = 50 * jbuff["right_y"]                                              # Y=ELŐRE
                if flags["flag_freeze_POS_Z"] == False:
                    directions["POS_Z"] = calc_POS_Z(directions, jbuff)
                elif flags["flag_freeze_POS_Z"] == True:
                    pass
                flgs["position_reached"] = False
                action = None
            elif flgs["flag_shiftActivated"] == True and flgs["flag_headModeSelected"] == False:       # HA SHIFT (Triangle button) aktív, akkor x,y mentén "eltolódik a robot, illetve Z tengely mentén fordúl
                directions["POS_X"] = 50 * jbuff["right_x"] 
                directions["POS_Y"] = 50 * jbuff["right_y"]
                directions["ROT_Y"] = 10 * jbuff["left_x"]                                               # ROT_Y=DÖL OLDLRA
                directions["POS_Z"] = calc_POS_Z(directions, jbuff)
                flgs["position_reached"] = False
                action = None
            elif flgs["flag_shiftActivated"] == False and flgs["flag_headModeSelected"] == True:
                directions["POS_X"] = 50 * jbuff["right_x"] 
                directions["POS_Y"] = 50 * jbuff["right_y"]
                directions["POS_Z"] = calc_POS_Z(directions, jbuff)

                head_in["headSide_diff"] = calc_HeadSidePos(jbuff)                                     # uses jbuff["left_x"]
                head_in["headBow_diff"] = calc_HeadBowPos(jbuff)                                       # uses jbuff["left_y"]
                flgs["position_reached"] = False
                action = None
                
            elif flgs["flag_shiftActivated"] == True and flgs["flag_headModeSelected"] == True:
                directions["POS_X"] = 50 * jbuff["right_x"] 
                directions["POS_Y"] = 50 * jbuff["right_y"]
                directions["ROT_Y"] = 10 * jbuff["left_x"]                                               # ROT_Y=DÖL OLDLRA
                directions["POS_Z"] = calc_POS_Z(directions, jbuff)
                head_in["headTwist_diff"] = calc_HeadTwistPos(jbuff)
                flgs["position_reached"] = False
                action = None
                    
        elif mode["mode"] == 3:
            if flgs["flag_shiftActivated"] == False:  
                directions["POS_X"] = 50 * jbuff["right_x"] 
                directions["POS_Y"] = 50 * jbuff["right_y"]
                directions["ROT_Z"] = 20 * jbuff["left_x"]
                if flags["flag_freeze_POS_Z"] == False:
                    directions["POS_Z"] = calc_POS_Z(directions, jbuff)
                elif flags["flag_freeze_POS_Z"] == True:
                    pass
                #directions["POS_Z"] = funct.calc_POS_Z(directions, jbuff)                                   # This section is commented out. POS_Z is modified by D-PAD UP/DOWN instead of R2 button during WALK mode  
                flgs["position_reached"] = False
                action = None
            elif flgs["flag_shiftActivated"] == True:  
                directions["POS_X"] = 50 * jbuff["right_x"] 
                directions["POS_Y"] = 50 * jbuff["right_y"]
                directions["ROT_X"] = 10 * jbuff["left_y"]
                directions["ROT_Y"] = 10 * jbuff["left_x"]
                if flags["flag_freeze_POS_Z"] == False:
                    directions["POS_Z"] = calc_POS_Z(directions, jbuff)
                elif flags["flag_freeze_POS_Z"] == True:
                    pass
                #directions["POS_Z"] = funct.calc_POS_Z(directions, jbuff)                                   # This section is commented out. POS_Z is modified by D-PAD UP/DOWN instead of R2 button during WALK mode  
                flgs["position_reached"] = False
                action = None

    elif action == "EMERGENCY_STOP":
        mode["EmgModeLvl"] = mode["EmgModeLvl"] + 1
        if mode["EmgModeLvl"] == 1:                               # go to EMERGENY MODE (mode = 10)
            mode["mode"] = 10
            flgs["position_reached"] = False
            action = None
        elif mode["EmgModeLvl"] == 2:                             # go back to IDLE mode and set IDLE position (like at the beginning of the program). Also clear idle counter
            mode["mode"] = 0
            print("FUNCT.: Leaving EMERGENCY MODE. Setting up IDLE...")
            flgs["position_reached"] = False
            flgs["return_to_idle"] = True
            mode["EmgModeLvl"] = 0
            action = None
    
    elif action == "SQUARE":
        if mode["mode"] == 2 or mode["mode"] == 3:
            if flags["flag_freeze_POS_Z"] == False:
                flags["flag_freeze_POS_Z"] = True
                print("FUNCT.: POS_Z freeze activated...")
            elif flags["flag_freeze_POS_Z"] == True:
                flags["flag_freeze_POS_Z"] = False
                print("FUNCT.: POS_Z freeze deactivated...")
    
def HxpdStateExecute(mode, flgs, stance, walkval, robot):
    """function: 
            Execute movements based on the HxpdStateSet() settings
        parameters:
            mode = points to a variable containing the actual / desired opMode of the robot
            flgs = points to the general "boolean status indicating" variable container
            stance = points to a variable containing the actual / desired value of robot stance
            walkVal = points to a dict. that contains auxilary variables to execute walk patterns
            robot = An instance of the class Heapod -> The robot itself (kematox)
        returns:
            None
    """
     # DPAD up/down -> POS_Z recalc -> IK_calc -> move  
    
    #print("Executing HxpdStateExecute()")

    if mode["mode"] == 0: # IDLE
        if flgs["position_reached"] == False:
            if flgs["return_to_Idle"] == True:
                print ("FUNCT.: Returning to IDLE")
                SetIdlePos(robot, "return")
                print ("FUNCT.: IDLE position reached\n")
                flgs["return_to_Idle"] = False
                flgs["position_reached"] = True
            
            elif flgs["return_to_Idle"] == False:
                print ("FUNCT.: MODE set to IDLE")                                  # ide még a fejet idle-be parancsot be kell szúrni
                SetIdlePos(robot, "set")
                print ("FUNCT.: IDLE position reached\n")
                flgs["position_reached"] = True
                
        elif flgs["position_reached"] == True:
            pass

    elif mode["mode"] == 1: # READY
        if flgs["position_reached"] == False:
            if flgs["return_to_Ready"] == True:
                print ("FUNCT.: Returning to READY")
                SetReadyPos(robot, "return", stance)
                CenterHead(robot)
                print ("FUNCT.: READY position reached\n")
                flgs["return_to_Ready"] = False
                flgs["position_reached"] = True
                
            elif flgs["return_to_Ready"] == False:
                print ("FUNCT.: MODE set to READY")
                SetReadyPos(robot, "set", stance)
                CenterHead(robot)
                print ("FUNCT.: READY position reached\n")
                flgs["position_reached"] = True
        elif flgs["position_reached"] == True:
            pass
        
    elif mode["mode"] == 2: # STATIC
        if flgs["flag_headModeSelected"] == False:
            if flgs["position_reached"] == False:
                IK.IK_SixLeg()
                robot.MoveSixLeg(None, "support")
                #IK.IK_Diag(IK.IK_out)
                if stance["setTo"] == "narrow":
                    DecresaeStance(robot, stanceVal)
                    stance["setTo"] = None
                elif stance["setTo"] == "wide":
                    IncreaseStance(robot, stanceVal)
                    stance["setTo"] = None
                flgs["position_reached"] = True
                print ("FUNCT.: MOVEMENT READY")
            elif flgs["position_reached"] == True:
                pass

        elif flgs["flag_headModeSelected"] == True:
            if flgs["position_reached"] == False:
                IK.IK_SixLeg()
                robot.MoveSixLeg(None, "support")
                IK.CalcHeadPos(HeadMovInput, HeadCalibrVal, HeadMovOutput)
                robot.MoveHead(HeadMovOutput, 500)
                #IK.IK_Diag(IK.IK_out)
                if stance["setTo"] == "narrow":
                    DecresaeStance(robot)
                    stance["setTo"] = None
                elif stance["setTo"] == "wide":
                    IncreaseStance(robot)
                    stance["setTo"] = None
                flgs["position_reached"] = True
                print ("FUNCT.: MOVEMENT READY")

        elif flgs["position_reached"] == True:
            pass
    
    elif mode["mode"] == 3: # WALK
        time.sleep(0.05)
        # EXECUTE WALK MOVEMENT PATTERNS
        WalkVector = IK.CalcWalkVector()
        #print "POS_X: " + str(IK.IK_in["POS_X"]) + "POS_Y: " + str(IK.IK_in["POS_Y"]) 
        #if ((abs(IK.IK_in["ROT_Z"]) > 0 and IK.IK_in["POS_Z"]) or (IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0)):
        if ((abs(IK.IK_in["ROT_Z"]) > 0 and IK.IK_in["POS_Z"]) or (WalkVector > 0 and IK.IK_in["POS_Z"] > 0) or (WalkVector > 0 and IK.IK_in["ROT_Y"] > 0 and IK.IK_in["POS_Z"] > 0)):
            #print "WALK"
            TripodWalk(robot, walkval, "Walk")
            flgs["flag_waswalking"] = True
            
        elif (IK.IK_in["POS_Z"] > 0 or IK.IK_in["ROT_Y"] > 0 or WalkVector >0 or (IK.IK_in["ROT_Y"] > 0 and WalkVector >0) or (IK.IK_in["POS_Z"] == 0 and IK.IK_in["ROT_Y"] == 0 and WalkVector == 0)): 
            """Akkor is STATIC legyen a mód, ha minden 0 -> visszatérjen a robot alaphelyzetbe """
            #print "STATIC"
            if flgs["flag_waswalking"] == True:
                flgs["flag_waswalking"] = False
                TripodWalk(robot, walkval, "Reset")
            
            if flgs["position_reached"] == False:
                IK.IK_SixLeg()
                robot.MoveSixLeg(None, "support")
                flgs["position_reached"] = True
                print ("DIAG: MOVEMENT READY")
            elif flgs["position_reached"] == True:
                pass 

        # EXECUTE Z AXIS TRANSLATION MOVEMENTS
        """if flgs["flag_DPAD_up"] == True:
            flgs["flag_DPAD_center"] = False
            while flgs["flag_DPAD_center"] == False:
                if IK.IK_in["POS_Z"] < 123.5:                               # Limited from calculated min value (0)
                    time.sleep(0.08)
                    IK.IK_in["POS_Z"] =  IK.IK_in["POS_Z"] + 3.25           # do z tanslation up
                    print (str(IK.IK_in["POS_Z"]))
                    IK.IK_SixLeg()
                    robot.MoveSixLeg(None, "support")
                    if HxpdStateSet.DPADReleased():
                        flgs["flag_DPAD_center"]: True
                        flgs["flag_DPAD_up"] = False
                        break
                    else:
                        continue

        elif flgs["flag_DPAD_down"] == True:
            flgs["flag_DPAD_center"] = False
            while flgs["flag_DPAD_center"] == False:
                if IK.IK_in["POS_Z"] > 6.5:                                 # Limited from calculated min value (0)
                    time.sleep(0.08)
                    IK.IK_in["POS_Z"] =  IK.IK_in["POS_Z"] - 3.25           # do z tanslation down
                    print (str(IK.IK_in["POS_Z"]))
                    IK.IK_SixLeg()
                    robot.MoveSixLeg(None, "support")
                    if HxpdStateSet.DPADReleased():
                        flgs["flag_DPAD_center"]: True
                        flgs["flag_DPAD_down"] = False
                        break
                    else:
                        continue"""

    elif mode["mode"] == 10:    #EMERGENCY MODE
        if flgs["position_reached"] == False:
            print("FUNCT.: !!! EMERGENY MODE !!! Release all servos")
            ReleaseAllServos(robot)
            flgs["position_reached"] = True
        else:
            pass

# """ MOVEMENT RELATED DEFINITIONS """
# SetIdlePos()
# SetReadyPos()
# IncreaseStance()
# DecreaseStance()
# TripodWalk()
# calc_HeadSidePos()
# calc_HeadBowPos()
# calc_HeadTwistPos()
# ReleaseAllServos()

def SetIdlePos(robot, mode):
    """Default value for idle stance is "D"=275, "z"=48"""
    if mode == "set":
        IK.IK_SixLeg()
        robot.MoveSixLeg(1500, "support")

    elif mode =="return":
        """STEP 1 - TRIPOD A lift legs"""
        IK.IK_in["POS_Z"] = -20.0
        IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....
        robot.MoveTripodA("default", "swing", 500)
       
        """STEP 2 - TRIPOD A lower leg to idle D position (275)"""
        IK.IK_in["D"] = 275.0
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_A("support")                       
        robot.MoveTripodA("default", "swing", 500)
        
        """STEP 3 - TRIPOD B lift legs"""
        IK.IK_in["D"] = 225.0
        IK.IK_in["POS_Z"] = -30.0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)
        
        """STEP 4 - TRIPOD B lower leg to idle D position (275)"""
        IK.IK_in["D"] = 275.0
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_B("support")
        robot.MoveTripodB("default", "swing", 500)
       
        """STEP 5 - lower body to idle position (z=48) """
        IK.IK_in["z"] = 48.0
        IK.IK_SixLeg()
        robot.MoveSixLeg(1500, "support")

def SetReadyPos(robot, mode, stance):
    """Default values for ready stance "D"=225, "z"=110"""
    if mode == "set":
        """STEP 1 - Robor lift"""
        IK.IK_in["z"] = 110.0
        IK.IK_SixLeg()
        robot.MoveSixLeg(750, "swing")
        """STEP 2 - TRIPOD A lift legs"""
        IK.IK_in["POS_Z"] = -50.0
        IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....
        robot.MoveTripodA("default", "swing", 500)
        """STEP 3 - TRIPOD A lower legs"""
        IK.IK_in["D"] = 225.0
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_A("support")                       
        robot.MoveTripodA("default", "swing", 500)
        """STEP 4 - TRIPOD B lift legs"""
        IK.IK_in["D"] = 275.0
        IK.IK_in["POS_Z"] = -50.0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)
        """STEP 5 - TRIPOD B lower legs"""
        IK.IK_in["D"] = 225.0
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)
        """STEP 6 - TRIPOD A lift legs again to release stress in servos"""
        IK.IK_in["POS_Z"] = -25.0
        IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....
        robot.MoveTripodA("default", "swing", 500)
        """STEP 7 - TRIPOD A lower legs"""
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_A("support")                       
        robot.MoveTripodA("default", "swing", 500)
        """STEP 8 - TRIPOD B lift legs again to release stress in servos"""
        IK.IK_in["POS_Z"] = -25.0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)
        """STEP 9 - TRIPOD B release legs"""
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)

        stance["stance"] = "default"
        
    elif mode == "return":
        """STEP 1 - return to default "z" at no matter what "D" value"""
        IK.IK_in["POS_Z"] = 0
        IK.IK_SixLeg()
        robot.MoveSixLeg(None, "swing")
        """STEP 2 - TRIPOD A lift legs"""
        IK.IK_in["POS_Z"] = -25.0
        IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....
        robot.MoveTripodA("default", "swing", 500)
        """STEP 3 - TRIPOD A lower legs. "D" is now equals id default value"""
        IK.IK_in["D"] = 225.0
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_A("support")                       
        robot.MoveTripodA("default", "swing", 500)
        """STEP 4 - TRIPOD B lift legs"""
        IK.IK_in["POS_Z"] = -25.0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)
        """STEP 5 - TRIPOD B lower legs"""
        IK.IK_in["POS_Z"] = 0
        IK.IK_Tripod_B("support")                       
        robot.MoveTripodB("default", "swing", 500)

        stance["stance"] = "default"

def IncreaseStance(robot, stance):
    """ function:
            Increase stance by 30mm 
        parameters:
            robot = An instance of the class Heapod -> The robot itself (kematox)
        returns: None
    """
    """STEP 1 - TRIPOD A lift legs"""
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....                     
    robot.MoveTripodA("default", "swing", 500)
    """STEP 2 - TRIPOD A lower legs"""
    IK.IK_in["D"] = 255.0
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_A("support")                     
    robot.MoveTripodA("default", "swing", 500)
    """STEP 4 - TRIPOD B lift legs"""
    IK.IK_in["D"] = 225.0
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_B("support")                     
    robot.MoveTripodB("default", "swing", 500)
    """STEP 5 - TRIPOD B lower legs"""
    IK.IK_in["D"] = 255.0
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_B("support")                     
    robot.MoveTripodB("default", "swing", 500)
    """STEP 6 - TRIPOD A lift legs again to release stress in servos"""
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....                     
    robot.MoveTripodA("default", "swing", 500)
    """STEP 7 - TRIPOD A lower legs"""
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_A("support")                     
    robot.MoveTripodA("default", "swing", 500)
    """STEP 8 - TRIPOD B lift legs again to release stress in servos"""
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_B("support")                     
    robot.MoveTripodB("default", "swing", 500)
    """STEP 9 - TRIPOD B release legs"""
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_B("support")                     
    robot.MoveTripodB("default", "swing", 500)
    if stance["stance"] == "default":
        stance["stance"] = "wide"
    elif stance["stance"] == "narrow":
        stance["stance"] = "default"

def DecresaeStance(robot, stance):
    """ function:
            Decrease stance by 30mm 
        parameters:
            robot = An instance of the class Heapod -> The robot itself (kematox)
        returns: None
    """
    """STEP 1 - TRIPOD A lift legs"""
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_A("support")                       # A "swing" az IK_in_for Swing- et használja....                    
    robot.MoveTripodA("default", "swing", 500)
    """STEP 2 - TRIPOD A lower legs"""
    IK.IK_in["D"] = 195.0
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_A("support")                    
    robot.MoveTripodA("default", "swing", 500)
    """STEP 3 - TRIPOD B lift legs"""
    IK.IK_in["D"] = 225.0
    IK.IK_in["POS_Z"] = -25.0
    IK.IK_Tripod_B("support")                    
    robot.MoveTripodB("default", "swing", 500)
    """STEP 4 - TRIPOD B lower legs"""
    IK.IK_in["D"] = 195.0
    IK.IK_in["POS_Z"] = 0
    IK.IK_Tripod_B("support")                    
    robot.MoveTripodB("default", "swing", 500)

    if stance["stance"] == "default":
        stance["stance"] = "narrow"
    elif stance["stance"] == "wide":
        stance["stance"] = "default"

def TripodWalk(robot, walkval, mode):                    
    """ Tripod walkpattern """
    def defineStepHeight():
        """ check POS_Z value to deifne step high. In idle pos no walking allowed,
        if POS_Z is below or equal with the half of max. POS_Z value than 25mm stepHigh is allowed
        if POS_Z is more than than the half of the alloewed value than 50mm stephigh is allowed """
        z_saved = 0.0                                       # Z pozició mentésére szolgáló változó. Az emelés után a láb ehhez a z-hez tartozó magasságba áljon vissza.
        
        if IK.IK_in["POS_Z"] == 0:                               
            stepHeight = 0.0                                       
            return stepHeight
        elif IK.IK_in["POS_Z"] <= 65:                       # Az analog érétkek kerekítettek (-1 és 1 között 0,1-es lépésekben) ->meghatározott  
            stepHeight = IK.IK_in["POS_Z"] - 25.0           # értéket vehet fel Z. ->az if feltételeket ehhez kell igazítani. Az 51 azért nem
            return stepHeight                               # müködött, mert ilyen értéket nem vehet fel Z ->mindig a nagyobb lépés teljesült...
        elif IK.IK_in["POS_Z"] > 65:                        # z lehetséges érétkei a pos_Hitec_to_JX.xls-ben találhatóak.
            stepHeight = IK.IK_in["POS_Z"] - 40.0                        
            return stepHeight
    
    if mode == "Walk":
        if walkval["tripod_step_1_complete"] == False:             
            # 1. TRIPOD A support body and translates
            IK.IK_Tripod_A("support")
            robot.MoveTripodA("default", "support", 500)      # time was 750
                
            # 2. TRIPOD B swigns -> raise and center TRIPOD B
            z_saved = IK.IK_in["POS_Z"]
            x_saved = IK.IK_in["POS_X"]
            y_saved = IK.IK_in["POS_Y"]
            rotz_saved = IK.IK_in["ROT_Z"]
            IK.IK_in["POS_Z"] = defineStepHeight()
            IK.IK_in["POS_X"] = 0.0
            IK.IK_in["POS_Y"] = 0.0
            IK.IK_in["ROT_Z"] = 0.0
            IK.IK_Tripod_B("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
            robot.MoveTripodB("default", "swing", 500)
                
            # 3. TRIPOD B swings -> lowering TRIPOD B
            IK.IK_in["POS_Z"] = z_saved
            
            IK.IK_in["POS_X"] = x_saved * -1                    # a nagyobb lépés érdekében nem 0-ra (alapállapotba) hozzuk vissza a lábat, hanem a x, y pozició "tükörképére"...
            IK.IK_in["POS_Y"] = y_saved * -1
            
            IK.IK_Tripod_B("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
            robot.MoveTripodB("default", "swing", 500)        #750
            
            IK.IK_in["POS_X"] = x_saved                        # rewrite original POS_X and POS_Y values to be able to calculate calcVector
            IK.IK_in["POS_Y"] = y_saved
            IK.IK_in["ROT_Z"] = rotz_saved
            
            walkval["tripod_step_1_complete"] = True
            
        elif walkval["tripod_step_1_complete"] == True:
            # 1. TRIPOD B support body and translates
            IK.IK_Tripod_B("support")
            robot.MoveTripodB("default", "support", 500)
                        
            # 2. TRIPOD A swigns -> raise TRIPOD A
            z_saved = IK.IK_in["POS_Z"]
            x_saved = IK.IK_in["POS_X"]
            y_saved = IK.IK_in["POS_Y"]
            rotz_saved = IK.IK_in["ROT_Z"]
            IK.IK_in["POS_Z"] = defineStepHeight()
            IK.IK_in["POS_X"] = 0.0                                 # new
            IK.IK_in["POS_Y"] = 0.0
            IK.IK_in["ROT_Z"] = 0.0
            IK.IK_Tripod_A("support")                             # !!! swing-nél a még a régi IK dict van használatban !!!
            robot.MoveTripodA("default", "swing", 500)
                
            # 3. TRIPOD A swings -> lowering TRIPOD A
            IK.IK_in["POS_Z"] = z_saved
            
            IK.IK_in["POS_X"] = x_saved * -1                    # a nagyobb lépés érdekében nem 0-ra (alapállapotba) hozzuk vissza a lábat, hanem a x, y pozició "tükörképére"...
            IK.IK_in["POS_Y"] = y_saved * -1
            
            IK.IK_Tripod_A("support")                             # !!! swing-nél a még a régi IK dict van használatban !!!
            robot.MoveTripodA("default", "swing", 500)         #750
            
            IK.IK_in["POS_X"] = x_saved
            IK.IK_in["POS_Y"] = y_saved
            IK.IK_in["ROT_Z"] = rotz_saved
            
            walkval["tripod_step_1_complete"] = False
            
    if mode == "Reset":
    
        z_saved = IK.IK_in["POS_Z"]
    
        IK.IK_in["POS_Z"] = defineStepHeight()
        IK.IK_in["POS_X"] = 0.0
        IK.IK_in["POS_Y"] = 0.0
        IK.IK_in["ROT_Z"] = 0.0
        IK.IK_Tripod_B("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
        robot.MoveTripodB("default", "swing", 500)
        
        IK.IK_in["POS_Z"] = z_saved
        IK.IK_Tripod_B("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
        robot.MoveTripodB("default", "swing", 500) 
        
        IK.IK_in["POS_Z"] = defineStepHeight()
        IK.IK_Tripod_A("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
        robot.MoveTripodA("default", "swing", 500)
        
        IK.IK_in["POS_Z"] = z_saved
        IK.IK_Tripod_A("support")                           # !!! swing-nél a még a régi IK dict van használatban !!!
        robot.MoveTripodA("default", "swing", 500)
    
def calc_HeadSidePos(jbuff):
    HeadSide_minVal = 60.0
    HeadSide_maxVal = 120.0
    joy_minVal = -1.0
    joy_maxVal = 1.0

    HeadSidePosVal = ((((HeadSide_maxVal - HeadSide_minVal) / (joy_maxVal - joy_minVal)) * jbuff["left_x"] * -1) + HeadSide_minVal) - HeadSide_minVal       # A -1-el valo szorzas azert van, hogy a fej a joy mozgással megegyezo iranyba mozduljon, ne invertalva
    return HeadSidePosVal

def calc_HeadBowPos(jbuff):
    HeadBow_minVal = 50.0
    HeadBow_maxVal = 140.0
    joy_minVal = -1.0
    joy_maxVal = 1.0

    HeadBowPosVal = ((((HeadBow_maxVal - HeadBow_minVal) / (joy_maxVal - joy_minVal)) * jbuff["left_y"] * -1) + HeadBow_minVal) - HeadBow_minVal            # A -1-el valo szorzas azert van, hogy a fej a joy mozgással megegyezo iranyba mozduljon, ne invertalva
    return HeadBowPosVal

def calc_HeadTwistPos(jbuff):
    HeadTwist_minVal = 60.0
    HeadTwist_maxVal = 120.0
    joy_minVal = -1.0
    joy_maxVal = 1.0

    HeadTwistPosVal = ((((HeadTwist_maxVal - HeadTwist_minVal) / (joy_maxVal - joy_minVal)) * jbuff["left_y"] * -1) + HeadTwist_minVal) - HeadTwist_minVal            # A -1-el valo szorzas azert van, hogy a fej a joy mozgással megegyezo iranyba mozduljon, ne invertalva
    return HeadTwistPosVal
    
    
def CenterHead(robot):
    IK.CalcHeadPos(HeadMovInput, HeadCalibrVal, HeadMovOutput)
    robot.MoveHead(HeadMovOutput, 500)
    
def ReleaseAllServos(robot):
    """ function:
          Release all servos. Used when Emergency button was uses (PS button), or when exiting the program 
          parameters: 
            robot = An instance of the class Heapod -> The robot itself (kematox)
          returns: None
    """
    #robot.SRVCTRL.Port.write("#0P0#1P0#2P0#8P0#9P0#10P0#4P0#5P0#6P0#16P0#18P0#19P0#24P0#25P0#26P0#20P0#21P0#22P0#29P0#30P0#31P0\r\n".encode()) # Release ALL servos
    #robot.SRVCTRL.Port.write("#0P0#1P0#2P0#24P0#25P0#26P0#4P0#5P0#6P0\r\n".encode())        # Release Tripod A
    #robot.SRVCTRL.Port.write("#16P0#18P0#19P0#8P0#9P0#10P0#20P0#21P0#22P0\r\n".encode())    # Release Tripod B
    #robot.SRVCTRL.Port.write("#29P0#30P0#31P0\r\n".encode())                                # Release Head
    robot.SRVCTRL.Port.write("#0P0#1P0#2P0#3P0#4P0#5P0#6P0#7P0#8P0#9P0#10P0#11P0#12P0#13P0#14P0#15P0#16P0#17P0#18P0#19P0#20P0#21P0#22P0#23P0#24P0#25P0#26P0#27P0#28P0#29P0#30P0#31P0\r\n".encode()) # Release ALL servos
