# -*- coding: utf-8 -*-
"""
#########################
LINUX VERSION use on RPi
#########################

Created on Fri Jan 26 21:29:41 2018
@author: Rozsee
"""
import serial  
#from copy import deepcopy
import RPi.GPIO as GPIO                                                      # GPIO-t kezelő modul importálása
GPIO.setmode(GPIO.BCM)        
#import pos
#import IK
from IK import IK_in, IK_out, HeadMovOutput, TripodA_MoveTable, TripodB_MoveTable

#walkVal = {"tripod_substep": 0, "walkmode": "TRIPOD", "def_tripod_step_1_complete": False, "def_tripod_step_2_complete": False}

"""CLASSES..."""
class Servo:
    def __init__(self, Servo_Id, Servo_Pos, SrvCtrl):                         # Minden létrehozott szervo példánynak legyen
        self.ID = Servo_Id                                                   # egy azonosítója (a leg-től kapja)
        self.Position = Servo_Pos                                             # egy pozicio értéke ms-ben (a leg-től kapja)
        self.SrvCtrl = SrvCtrl

    def SetServoPosition(self):
        """Egy láb tetszőleges szervóját mozgatja."""
        self.SrvCtrl.SetToMove("#" + str(self.ID) + "P" + str(self.Position)) 
    
                                                        
class Leg:
    def __init__(self, servo_param_dict, SrvCtrl):                            # Létrehozzuk a lához tartozó szervó példányokat
        self.Name = servo_param_dict.get("name")
        self.Coxa = Servo(servo_param_dict.get("id_coxa"), servo_param_dict.get("pos_coxa"), SrvCtrl)
        self.Femur = Servo(servo_param_dict.get("id_femur"), servo_param_dict.get("pos_femur"), SrvCtrl)
        self.Tibia = Servo(servo_param_dict.get("id_tibia"), servo_param_dict.get("pos_tibia"), SrvCtrl)
        GPIO.setup(servo_param_dict.get("GPIO"), GPIO.IN)                    # Setup footswitch GPIO port to IN
        self.FootSwitch = servo_param_dict.get("GPIO")
    

    def updatePosition(self, posDict):
        self.Coxa.Position = posDict["pos_coxa"]
        self.Femur.Position = posDict["pos_femur"]
        self.Tibia.Position = posDict["pos_tibia"]


    def SetLegPosition(self):
        Servo.SetServoPosition(self.Coxa)
        Servo.SetServoPosition(self.Femur)
        Servo.SetServoPosition(self.Tibia)


class Head:        
    def __init__(self, servo_param_dict, SrvCtrl):
        """ Creates an instance of the HEAD object """
        self.Name = servo_param_dict.get("name")
        self.HeadBow = Servo(servo_param_dict.get("id_head_bow"), servo_param_dict.get("pos_HeadBow"), SrvCtrl)
        self.HeadTwst = Servo(servo_param_dict.get("id_head_twst"), servo_param_dict.get("pos_HeadTwst"), SrvCtrl)
        self.HeadSideMov = Servo(servo_param_dict.get("id_head_sideMov"), servo_param_dict.get("pos_HeadSideMov"), SrvCtrl)
    
    def updatePosition(self, posDict):
        """ Refereshes the posiions of the servos from the dictonary that contains the actual position values """
        self.HeadBow.Position = posDict["pos_headBow"]
        self.HeadTwst.Position = posDict["pos_headTwist"]
        self.HeadSideMov.Position = posDict["pos_headSide"]

    def SetHeadPosition(self):
        """ Cals servo definition to create command string to Servo Controller """
        Servo.SetServoPosition(self.HeadBow)
        Servo.SetServoPosition(self.HeadTwst)
        Servo.SetServoPosition(self.HeadSideMov)

          
class SrvCtrl(object):
    """ Szervo kontroller objektum. A SSC32 számára állítja össze a parancs sztringet és 
    küldi ki azt a soros porton."""
    Name = None
    CmdBuf = None
    Port = None

    def __init__(self, name):
        self.Name = name
        self.CmdBuf = ""
        self.Port = serial.Serial('/dev/serial0', 115200, timeout = 0.06)              # LINUXHOZ: serial.Serial('/dev/ttyAMA0', 115200, timeout = 1) comport was 3

    def SetToMove(self, cmd_string):
        """ A paraméterként megadott stringet mindíg hozzáadjuk a CmdBuf-hoz """
        self.CmdBuf = self.CmdBuf + cmd_string


    def ExecuteMove(self, MoveTime, querry):
        """ ExecuteMove-al adjuk hozzá a CmdBuf-hoz a mozgatási időt (le-
        zárva a parancs szringet) és küldjük ki soros porton a  parancsot
        szervovezérlőnek ezzel indítva a mozgás végrehajtását """
        defMoveTime = 750                                               # was 750 
        if MoveTime == None:
            self.CmdBuf = self.CmdBuf + "T" + str(defMoveTime) + "\r\n"
            #print "SRVCTRL in: " + self.CmdBuf
            self.Port.write(self.CmdBuf)
            if querry == "Poll":
                print ("SSC32: Polling SRVCNTRL till movement finished... Using default movetime...")
                while True:
                    self.Port = "Q\r\n"
                    resp = self.Port.readline()
                    print ("SRVCTRL out: " + resp)
                    if resp == ".":
                        break
                self.CmdBuf = ""
            elif querry == "NoPoll":
                print ("SSC32: Polling turned OFF! Using default movetime...")
                self.CmdBuf = ""
        else:
            self.CmdBuf = self.CmdBuf + "T" + str(MoveTime) + "\r\n"
            #print "SRVCTRL in: " + self.CmdBuf
            self.Port.write(self.CmdBuf)
            if querry == "Poll":
                print ("SSC32: Polling SRVCNTRL movement finished... Using preset/calc. movetime")
                while True:
                    self.Port.write("Q\r\n")
                    resp = self.Port.readline()
                    print ("SRVCTRL out: " + resp)
                    if resp == ".":
                        break
                self.CmdBuf = ""     
            elif querry == "NoPoll":
                print ("SSC32: Polling turned OFF! Using preset/calc. movetime.")
                self.CmdBuf = ""


class Hexapod(object):
    servo_param_dict = None                                                  # ezek a osztályváltozók ide nem kötelezően kelenek. Működik e nélkül is,
    Name = None                                                              # az osztályváltozók felsorolása az osztály öröklésnél fontos
    RF = None
    RM = None
    RR = None
    LF = None
    LM = None
    LR = None
    HEAD = None
    SRVCTRL = None    
    
    def __init__(self, name):
        self.servo_param_dict = {
                "RF": {"name": "RF", "GPIO": 17, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur": 1, "id_tibia": 2, "id_coxa": 0, "chngd": 0},  # Right front leg (CON:2); femur = felsö labsz, tibia = also labsz.
                "RM": {"name": "RM", "GPIO": 27, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur": 9, "id_tibia":10, "id_coxa": 8, "chngd": 0},  # Right middle leg (CON:4)
                "RR": {"name": "RR", "GPIO": 22, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur": 5, "id_tibia": 6, "id_coxa": 4, "chngd": 0},  # Right rear leg (CON:6)
                "LF": {"name": "LF", "GPIO": 23, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur":19, "id_tibia":18, "id_coxa":16, "chngd": 0},  # Left front leg (CON:1); id_femur was 17
                "LM": {"name": "LM", "GPIO": 24, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur":25, "id_tibia":26, "id_coxa":24, "chngd": 0},  # Left middle leg (CON:3)
                "LR": {"name": "LR", "GPIO": 25, "pos_femur": None, "pos_tibia": None, "pos_coxa": None, "id_femur":21, "id_tibia":22, "id_coxa":20, "chngd": 0},  # Left rear leg (CON:5)
                "HEAD": {"name": "HEAD", "pos_head_bow": None, "pos_head_twst": None, "pos_head_siedMov": None, "id_head_bow": 31, "id_head_twst": 30, "id_head_sideMov": 29, "chngd": 0}                                                                              # Dict. for Head parameters
                }                                                            # Az összes végtag paraméterét tartalmazo dict. Az egyes lábak külön dict-be rendezve a dict-en belül
        
        self.Name = name
        self.SRVCTRL = SrvCtrl("SSC32") 
        self.RF = Leg(self.servo_param_dict["RF"], self.SRVCTRL)             # Leg példányok létrehozása a param_dict dictonary megfelelő adataival A.) módon
        self.RM = Leg(self.servo_param_dict.get("RM"), self.SRVCTRL)         # Leg példányok létrehozása a param_dict dictonary megfelelő adataival B.) módon
        self.RR = Leg(self.servo_param_dict.get("RR"), self.SRVCTRL)         # többszintű dictonary kulcsainak és értékeinek elérése a get() funkcióval, vagy "manuálisan": outer_dictname[inner_dictname][inner_dictname_value]
        self.LF = Leg(self.servo_param_dict.get("LF"), self.SRVCTRL)
        self.LM = Leg(self.servo_param_dict.get("LM"), self.SRVCTRL)
        self.LR = Leg(self.servo_param_dict.get("LR"), self.SRVCTRL)
        self.HEAD = Head(self.servo_param_dict.get("HEAD"), self.SRVCTRL)
        #return self # csak az init után kell return self-et alkalmazni.        
        

    def Update_Spdict(self, input_dict, legs_select, leg_mode, steptime):
        """ Az egyes lábakhoz tartozó szervo poziciókat frissíti az új pozíció
        értékekkel, melyeket az input_dict[] tartalmaz. 
        FONTOS: nem a servo_param_dict-et
        frssitjük (mint ami az eredeti elképzelés volt, mert ugyan az objektumokat a
        servo_param_dict segítségével hoztuk létre, de ha modosúl a servo_param_dict
        dictonary, attol még az objektumokban az értékek nem frissülnek maguktól.
        Erre kell a Leg.updatePosition metódus"""
        if legs_select == "all":
            self.RF.updatePosition(input_dict["RF"])
            self.RM.updatePosition(input_dict["RM"])
            self.RR.updatePosition(input_dict["RR"])
            self.LF.updatePosition(input_dict["LF"])
            self.LM.updatePosition(input_dict["LM"])
            self.LR.updatePosition(input_dict["LR"])
            if leg_mode == "swing":
                self.SetLegsPosition("all")
                self.SRVCTRL.ExecuteMove(steptime, "Poll")
            elif leg_mode == "support":
                self.SetLegsPosition("all")
                self.SRVCTRL.ExecuteMove(steptime, "NoPoll")

        elif legs_select == "TripodA":
            self.RF.updatePosition(input_dict["RF"])
            self.LM.updatePosition(input_dict["LM"])
            self.RR.updatePosition(input_dict["RR"])
            if leg_mode == "swing":
                self.SetLegsPosition("TripodA")
                self.SRVCTRL.ExecuteMove(steptime, "Poll")
            elif leg_mode == "support":
                self.SetLegsPosition("TripodA")
                self.SRVCTRL.ExecuteMove(steptime, "NoPoll")

        elif legs_select == "TripodB":
            self.LF.updatePosition(input_dict["LF"])
            self.RM.updatePosition(input_dict["RM"])
            self.LR.updatePosition(input_dict["LR"])
            if leg_mode == "swing":
                self.SetLegsPosition("TripodB")
                self.SRVCTRL.ExecuteMove(steptime, "Poll")
            elif leg_mode == "support":
                self.SetLegsPosition("TripodB")
                self.SRVCTRL.ExecuteMove(steptime, "NoPoll")


    def SetLegsPosition(self, legs_select):
        """ Az egyes lábakat felépító szervo példányok pozicióját beállítja a 
        servo_param_dict-ben tárolt pozició adatok szerint és legyártja a 
        parancs stringet """
        if legs_select == "all":
            self.RF.SetLegPosition()
            self.RM.SetLegPosition()
            self.RR.SetLegPosition()
            self.LF.SetLegPosition()
            self.LM.SetLegPosition()
            self.LR.SetLegPosition()
            #print "SetLegsPosition - all lefutott" 

        elif legs_select == "TripodA":
            self.RF.SetLegPosition()
            self.LM.SetLegPosition()
            self.RR.SetLegPosition()

        elif legs_select == "TripodB":
            self.LF.SetLegPosition()
            self.RM.SetLegPosition()
            self.LR.SetLegPosition()        

       
    def MoveSixLeg(self, MoveTime, mode):
        if MoveTime == None:
            if mode == "support":
                self.Update_Spdict(IK_out, "all", "support", 500)                         # time was 750ms, mode was swing -> each new position was waited to be executed 
            elif mode == "swing":
                self.Update_Spdict(IK_out, "all", "swing", 500)
        else:
            if mode == "support":
                self.Update_Spdict(IK_out, "all", "support", MoveTime)                         # time was 750ms, mode was swing -> each new position was waited to be executed 
            elif mode == "swing":
                self.Update_Spdict(IK_out, "all", "swing", MoveTime)


    def MoveTripodA(self, gate, mode, StepTime):
        if gate == "default":
            if mode == "support":
                self.Update_Spdict(TripodA_MoveTable, "TripodA", "support", StepTime)
            elif mode == "swing":
                print ("Most emelem A-t!")
                self.Update_Spdict(TripodA_MoveTable, "TripodA", "swing", StepTime / 2)
        elif gate == "wave":
            pass


    def MoveTripodB(self, gate, mode, StepTime):
        if gate == "default":
            if mode == "support":
                print ("Most tartom B-t!")
                self.Update_Spdict(TripodB_MoveTable, "TripodB", "support", StepTime)
            elif mode == "swing":
                print ("Most emelem B-t!")
                self.Update_Spdict(TripodB_MoveTable, "TripodB", "swing", StepTime / 2)
        elif gate == "wave":
            pass


    def TransferHeadPosToSrvoCtrl(self, headpos, movetime):
            self.HEAD.updatePosition(headpos)
            self.HEAD.SetHeadPosition()
            print ("mozgatoma a fejet")
            self.SRVCTRL.ExecuteMove(movetime, "NoPoll")  


    def MoveHead(self, headservopos, movetime):
        self.TransferHeadPosToSrvoCtrl(headservopos, movetime)

    """
    def LegFeetToGround(self, leg):
        pass
    
    def TripodFeetToGround(self, tripod):
        pass
    """