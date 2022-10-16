# coding=utf-8
"""
#########################
LINUX VERSION use on RPi
#########################
"""

from math import sqrt, pow, degrees, radians, sin, cos, tan, acos, atan, atan2
from copy import deepcopy

IK_in = {"POS_X": 0.0, "POS_Y": 0.0, "POS_Z": 0.0, "ROT_X": 0.0, "ROT_Y": 0.0, "ROT_Z": 0.0, "D": 275.0, "z": 48.0}                     #225.0
HeadMovInput = {"headBow_def": 90, "headTwist_def": 90, "headSide_def": 90,
                "headBow_diff": 0, "headTwist_diff": 0, "headSide_diff":0,
                "headBow_mod": 0, "headTwist_mod": 0, "headSide_mod":0}                                                                 # Head servo poziciók fokban megadva (kezdo, különbség, vegso ertek) (bemenő paraméterek) 
HeadMovOutput = {"pos_headBow": 0, "pos_headTwist": 0, "pos_headSide": 0}                                                               # Head servo pozíciók ms-ba átszámolva (kimenő paraméterek)
HeadCalibrVal = {"pos_headBow": 50, "pos_headTwist": -80, "pos_headSide": 50}                                                           # Servo calibration values to add the calculated values
IK_in_for_Swing = {"POS_X": 0 , "POS_Y": 0, "POS_Z": 0, "ROT_X": 0, "ROT_Y": 0, "ROT_Z": 0, "D": 225.0}                                 #225.0 is the default value 260 id for experimental purposes to cgange main stance

ConstantVal = { "dist_center_corncoxa": 121.0,
                "dist_center_midcoxa": 101.0,
                "lCoxa": 52.17,
                "lFemur": 75.0,
                "lTibia": 165.9,                 # was 187.35. Modified to 165.9 after tibia servos were flipped
                "angCornCoxa": 51.0,
                "angMidCoxa": 0.0,
                "z_offset_def": 138.55 #110.0     # 160.0 is the default walue. 110.0 is for experimental purposes to change main stance.
                                                  # The default valu had to be modified with 21,45 (160-21,45=138,55) in order to not to 
                                                  # have movement on Z axis when changing from pre calculated positions (pos.py) to calcualted
                                                  # positions
              }

SrvoCalibrVal = {                                                               # Servo calibration values to modify the calculated servo positions
                    "RF": {"pos_coxa":  90, "pos_femur":  50, "pos_tibia": -40},
                    "RM": {"pos_coxa": -30, "pos_femur":  10, "pos_tibia":   0},
                    "RR": {"pos_coxa": -30, "pos_femur":  10, "pos_tibia": -10},
                    "LF": {"pos_coxa":  10, "pos_femur": -30, "pos_tibia":  80},
                    "LM": {"pos_coxa": -20, "pos_femur": -10, "pos_tibia":  60},
                    "LR": {"pos_coxa":   0, "pos_femur": -30, "pos_tibia": -10}
                }
              
IK_out = {
          "RF": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
          "RM": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
          "RR": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
          "LF": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
          "LM": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
          "LR": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0}
         }
         
TripodA_MoveTable = {
                    "RF": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
                    "LM": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
                    "RR": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0}
                    }
                    
TripodB_MoveTable = {
                    "LF": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
                    "RM": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0},
                    "LR": {"pos_coxa": 0, "pos_femur": 0, "pos_tibia": 0}
                    }
         
         
         

def IK(leg_ID, input_dict, const_dict, calibr_dict, output_dict):
    CoxaCoord = {
                    "RF": {"dCntr_RFC_X": 75.78, "dCntr_RFC_Y": 94.35},
                    "RM": {"dCntr_RMC_X": 100.95, "dCntr_RMC_Y": 0},
                    "RR": {"dCntr_RRC_X": 75.78, "dCntr_RRC_Y": -94.35},
                    "LF": {"dCntr_LFC_X": -75.78, "dCntr_LFC_Y": 94.35},
                    "LM": {"dCntr_LMC_X": -100.95, "dCntr_LMC_Y": 0},
                    "LR": {"dCntr_LRC_X": -75.78, "dCntr_LRC_Y": -94.35}
                }
                
    FeetPosVal = {
                    "RF": {"RF_FeetPos_X": 0, "RF_FeetPos_Y": 0, "RF_FeetPos_Z": 0},
                    "RM": {"RM_FeetPos_X": 0, "RM_FeetPos_Y": 0, "RM_FeetPos_Z": 0},
                    "RR": {"RR_FeetPos_X": 0, "RR_FeetPos_Y": 0, "RR_FeetPos_Z": 0},
                    "LF": {"LF_FeetPos_X": 0, "LF_FeetPos_Y": 0, "LF_FeetPos_Z": 0},
                    "LM": {"LM_FeetPos_X": 0, "LM_FeetPos_Y": 0, "LM_FeetPos_Z": 0},
                    "LR": {"LR_FeetPos_X": 0, "LR_FeetPos_Y": 0, "LR_FeetPos_Z": 0}
                 }
              
    LegTotalVal = {
                    "RF": {"RF_Total_X": 0, "RF_Total_Y": 0, "RF_Total_Z": 0, "RF_TotDist_cntr_legend": 0, "RF_AngBdyCntr_X": 0},
                    "RM": {"RM_Total_X": 0, "RM_Total_Y": 0, "RM_Total_Z": 0, "RM_TotDist_cntr_legend": 0, "RM_AngBdyCntr_X": 0},
                    "RR": {"RR_Total_X": 0, "RR_Total_Y": 0, "RR_Total_Z": 0, "RR_TotDist_cntr_legend": 0, "RR_AngBdyCntr_X": 0},
                    "LF": {"LF_Total_X": 0, "LF_Total_Y": 0, "LF_Total_Z": 0, "LF_TotDist_cntr_legend": 0, "LF_AngBdyCntr_X": 0},
                    "LM": {"LM_Total_X": 0, "LM_Total_Y": 0, "LM_Total_Z": 0, "LM_TotDist_cntr_legend": 0, "LM_AngBdyCntr_X": 0},
                    "LR": {"LR_Total_X": 0, "LR_Total_Y": 0, "LR_Total_Z": 0, "LR_TotDist_cntr_legend": 0, "LR_AngBdyCntr_X": 0}
                  }
            
    RollPitchVal = {
                    "RF": {"RF_Roll_Y": 0, "RF_Pitch_X": 0, "RF_Yaw_Z": 0},
                    "RM": {"RM_Roll_Y": 0, "RM_Pitch_X": 0, "RM_Yaw_Z": 0},
                    "RR": {"RR_Roll_Y": 0, "RR_Pitch_X": 0, "RR_Yaw_Z": 0},
                    "LF": {"LF_Roll_Y": 0, "LF_Pitch_X": 0, "LF_Yaw_Z": 0},
                    "LM": {"LM_Roll_Y": 0, "LM_Pitch_X": 0, "LM_Yaw_Z": 0},
                    "LR": {"LR_Roll_Y": 0, "LR_Pitch_X": 0, "LR_Yaw_Z": 0}
                   }
                   
    BodyIKVal = {
                "RF": {"RF_BodyIK_X": 0, "RF_BodyIK_Y": 0, "RF_BodyIK_Z": 0},
                "RM": {"RM_BodyIK_X": 0, "RM_BodyIK_Y": 0, "RM_BodyIK_Z": 0},
                "RR": {"RR_BodyIK_X": 0, "RR_BodyIK_Y": 0, "RR_BodyIK_Z": 0},
                "LF": {"LF_BodyIK_X": 0, "LF_BodyIK_Y": 0, "LF_BodyIK_Z": 0},
                "LM": {"LM_BodyIK_X": 0, "LM_BodyIK_Y": 0, "LM_BodyIK_Z": 0},
                "LR": {"LR_BodyIK_X": 0, "LR_BodyIK_Y": 0, "LR_BodyIK_Z": 0}
             }
             
    NewPos = {
                "RF": {"RF_NewPos_X": 0, "RF_NewPos_Y": 0, "RF_NewPos_Z": 0},
                "RM": {"RM_NewPos_X": 0, "RM_NewPos_Y": 0, "RM_NewPos_Z": 0},
                "RR": {"RR_NewPos_X": 0, "RR_NewPos_Y": 0, "RR_NewPos_Z": 0},
                "LF": {"LF_NewPos_X": 0, "LF_NewPos_Y": 0, "LF_NewPos_Z": 0},
                "LM": {"LM_NewPos_X": 0, "LM_NewPos_Y": 0, "LM_NewPos_Z": 0},
                "LR": {"LR_NewPos_X": 0, "LR_NewPos_Y": 0, "LR_NewPos_Z": 0}
             }
             
    LegAuxVal = {
                    "RF": {"RF_DistCoxaLegend": 0, "RF_L": 0},
                    "RM": {"RM_DistCoxaLegend": 0, "RM_L": 0},
                    "RR": {"RR_DistCoxaLegend": 0, "RR_L": 0},
                    "LF": {"LF_DistCoxaLegend": 0, "LF_L": 0},
                    "LM": {"LM_DistCoxaLegend": 0, "LM_L": 0},
                    "LR": {"LR_DistCoxaLegend": 0, "LR_L": 0} 
                }
             
    TrgAngVal = {
                    "RF": {"RF_Alpha1": 0, "RF_Alpha2": 0, "RF_Beta": 0},
                    "RM": {"RM_Alpha1": 0, "RM_Alpha2": 0, "RM_Beta": 0},
                    "RR": {"RR_Alpha1": 0, "RR_Alpha2": 0, "RR_Beta": 0},
                    "LF": {"LF_Alpha1": 0, "LF_Alpha2": 0, "LF_Beta": 0},
                    "LM": {"LM_Alpha1": 0, "LM_Alpha2": 0, "LM_Beta": 0},
                    "LR": {"LR_Alpha1": 0, "LR_Alpha2": 0, "LR_Beta": 0}
                }
    
    RawAngVal = {
                    "RF": {"RF_CoxaAng": 0, "RF_FemurAng": 0, "RF_TibiaAng": 0},
                    "RM": {"RM_CoxaAng": 0, "RM_FemurAng": 0, "RM_TibiaAng": 0},
                    "RR": {"RR_CoxaAng": 0, "RR_FemurAng": 0, "RR_TibiaAng": 0},
                    "LF": {"LF_CoxaAng": 0, "LF_FemurAng": 0, "LF_TibiaAng": 0},
                    "LM": {"LM_CoxaAng": 0, "LM_FemurAng": 0, "LM_TibiaAng": 0},
                    "LR": {"LR_CoxaAng": 0, "LR_FemurAng": 0, "LR_TibiaAng": 0}
                }

    RawAngRecalc =  {
                    "RF": {"RF_CoxaAng": 0, "RF_FemurAng": 0, "RF_TibiaAng": 0},
                    "RM": {"RM_CoxaAng": 0, "RM_FemurAng": 0, "RM_TibiaAng": 0},
                    "RR": {"RR_CoxaAng": 0, "RR_FemurAng": 0, "RR_TibiaAng": 0},
                    "LF": {"LF_CoxaAng": 0, "LF_FemurAng": 0, "LF_TibiaAng": 0},
                    "LM": {"LM_CoxaAng": 0, "LM_FemurAng": 0, "LM_TibiaAng": 0},
                    "LR": {"LR_CoxaAng": 0, "LR_FemurAng": 0, "LR_TibiaAng": 0}
                    }                 
                  
            
    def LegEndPoint (leg_ID, const_dict, input_dict, coord_dict):
        def X_coord(leg_ID, const_dict, input_dict, coord_dict):
            if leg_ID == "RF":
                x = cos(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["RF"]["RF_FeetPos_X"] = x 
                
            elif leg_ID == "RM":
                x = input_dict["D"] - const_dict["dist_center_midcoxa"]
                coord_dict["RM"]["RM_FeetPos_X"] = x 
                
            elif leg_ID == "RR":
                x = cos(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["RR"]["RR_FeetPos_X"] = x 
                
            elif leg_ID == "LF":
                x = -1 * cos(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["LF"]["LF_FeetPos_X"] = x 
                
            elif leg_ID == "LM":
                x = -1*(input_dict["D"] - const_dict["dist_center_midcoxa"])
                coord_dict["LM"]["LM_FeetPos_X"] = x 
            
            elif leg_ID == "LR":    
                x = -1 * cos(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["LR"]["LR_FeetPos_X"] = x 
                
        def Y_coord(leg_ID, const_dict, input_dict, coord_dict):
            if leg_ID == "RF":
                y = sin(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["RF"]["RF_FeetPos_Y"] = y 
                
            elif leg_ID == "RM":
                y = 0.0
                coord_dict["RM"]["RM_FeetPos_Y"] = y
                
            elif leg_ID == "RR":
                y = sin(radians(const_dict["angCornCoxa"]) * -1) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["RR"]["RR_FeetPos_Y"] = y
                
            elif leg_ID == "LF":
                y = sin(radians(const_dict["angCornCoxa"])) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["LF"]["LF_FeetPos_Y"] = y
                
            elif leg_ID == "LM":
                y = 0.0
                coord_dict["LM"]["LM_FeetPos_Y"] = y
                
            elif leg_ID == "LR":    
                y = sin(radians(const_dict["angCornCoxa"]) * -1) * (input_dict["D"] - const_dict["dist_center_corncoxa"])
                coord_dict["LR"]["LR_FeetPos_Y"] = y
                
        def Z_coord(leg_ID, const_dict, input_dict, coord_dict):
            if leg_ID == "RF":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["RF"]["RF_FeetPos_Z"] = z
                
            elif leg_ID == "RM":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["RM"]["RM_FeetPos_Z"] = z
                
            elif leg_ID == "RR":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["RR"]["RR_FeetPos_Z"] = z
                
            elif leg_ID == "LF":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["LF"]["LF_FeetPos_Z"] = z
                
            elif leg_ID == "LM":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["LM"]["LM_FeetPos_Z"] = z
                
            elif leg_ID == "LR":
                z = input_dict["z"]
                #z = const_dict["z_offset_def"]
                coord_dict["LR"]["LR_FeetPos_Z"] = z
            
        X_coord(leg_ID, const_dict, input_dict, coord_dict)
        Y_coord(leg_ID, const_dict, input_dict, coord_dict)
        Z_coord(leg_ID, const_dict, input_dict, coord_dict)
        
            
    def LegTotal(leg_ID, input_dict, cCoord_dict, coord_dict, total_dict):
        def Total_X(leg_ID, input_dict, cCoord_dict, coord_dict, total_dict):
            if leg_ID == "RF":
                tx = coord_dict["RF"]["RF_FeetPos_X"] + cCoord_dict["RF"]["dCntr_RFC_X"] + input_dict["POS_X"]
                total_dict["RF"]["RF_Total_X"] = tx
                
            elif leg_ID =="RM":
                tx = coord_dict["RM"]["RM_FeetPos_X"] + cCoord_dict["RM"]["dCntr_RMC_X"] + input_dict["POS_X"]
                total_dict["RM"]["RM_Total_X"] = tx
                
            elif leg_ID == "RR":
                tx = coord_dict["RR"]["RR_FeetPos_X"] + cCoord_dict["RR"]["dCntr_RRC_X"] + input_dict["POS_X"]
                total_dict["RR"]["RR_Total_X"] = tx
                
            elif leg_ID == "LF":
                tx = coord_dict["LF"]["LF_FeetPos_X"] + cCoord_dict["LF"]["dCntr_LFC_X"] + input_dict["POS_X"]
                total_dict["LF"]["LF_Total_X"] = tx
                
            elif leg_ID == "LM":
                tx = coord_dict["LM"]["LM_FeetPos_X"] + cCoord_dict["LM"]["dCntr_LMC_X"] + input_dict["POS_X"]
                total_dict["LM"]["LM_Total_X"] = tx
                
            elif leg_ID == "LR":
                tx = coord_dict["LR"]["LR_FeetPos_X"] + cCoord_dict["LR"]["dCntr_LRC_X"] + input_dict["POS_X"]
                total_dict["LR"]["LR_Total_X"] = tx
                
        def Total_Y(leg_ID, input_dict, cCoord_dict, coord_dict, total_dict):
            if leg_ID == "RF":
                ty = coord_dict["RF"]["RF_FeetPos_Y"] + cCoord_dict["RF"]["dCntr_RFC_Y"] + input_dict["POS_Y"]
                total_dict["RF"]["RF_Total_Y"] = ty
                
            elif leg_ID =="RM":
                ty = coord_dict["RM"]["RM_FeetPos_Y"] + cCoord_dict["RM"]["dCntr_RMC_Y"] + input_dict["POS_Y"]
                total_dict["RM"]["RM_Total_Y"] = ty
                
            elif leg_ID == "RR":
                ty = coord_dict["RR"]["RR_FeetPos_Y"] + cCoord_dict["RR"]["dCntr_RRC_Y"] + input_dict["POS_Y"]
                total_dict["RR"]["RR_Total_Y"] = ty
                
            elif leg_ID == "LF":
                ty = coord_dict["LF"]["LF_FeetPos_Y"] + cCoord_dict["LF"]["dCntr_LFC_Y"] + input_dict["POS_Y"]
                total_dict["LF"]["LF_Total_Y"] = ty
                
            elif leg_ID == "LM":
                ty = coord_dict["LM"]["LM_FeetPos_Y"] + cCoord_dict["LM"]["dCntr_LMC_Y"] + input_dict["POS_Y"]
                total_dict["LM"]["LM_Total_Y"] = ty
                
            elif leg_ID == "LR":
                ty = coord_dict["LR"]["LR_FeetPos_Y"] + cCoord_dict["LR"]["dCntr_LRC_Y"] + input_dict["POS_Y"]
                total_dict["LR"]["LR_Total_Y"] = ty
                
          
          
        def Total_Z(leg_ID, input_dict, coord_dict, total_dict):
            if leg_ID == "RF":
                tz = coord_dict["RF"]["RF_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["RF"]["RF_Total_Z"] = tz
                
            elif leg_ID == "RM":
                tz = coord_dict["RM"]["RM_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["RM"]["RM_Total_Z"] = tz
                
            elif leg_ID == "RR":
                tz = coord_dict["RR"]["RR_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["RR"]["RR_Total_Z"] = tz    
            
            elif leg_ID == "LF":
                tz = coord_dict["LF"]["LF_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["LF"]["LF_Total_Z"] = tz    
            
            elif leg_ID == "LM":
                tz = coord_dict["LM"]["LM_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["LM"]["LM_Total_Z"] = tz  
                
            elif leg_ID == "LR":
                tz = coord_dict["LR"]["LR_FeetPos_Z"] + input_dict["POS_Z"]
                total_dict["LR"]["LR_Total_Z"] = tz      
                
            
            
        def TotDist_cntr_legend(leg_ID, total_dict):
            if leg_ID == "RF":
                totDist = sqrt(pow(total_dict["RF"]["RF_Total_X"],2) + pow(total_dict["RF"]["RF_Total_Y"],2))
                total_dict["RF"]["RF_TotDist_cntr_legend"] = totDist
                
            elif leg_ID =="RM":
                totDist = sqrt(pow(total_dict["RM"]["RM_Total_X"],2) + pow(total_dict["RM"]["RM_Total_Y"],2))
                total_dict["RM"]["RM_TotDist_cntr_legend"] = totDist
                
            elif leg_ID == "RR":
                totDist = sqrt(pow(total_dict["RR"]["RR_Total_X"],2) + pow(total_dict["RR"]["RR_Total_Y"],2))
                total_dict["RR"]["RR_TotDist_cntr_legend"] = totDist
                
            elif leg_ID == "LF":
                totDist = sqrt(pow(total_dict["LF"]["LF_Total_X"],2) + pow(total_dict["LF"]["LF_Total_Y"],2))
                total_dict["LF"]["LF_TotDist_cntr_legend"] = totDist
                
            elif leg_ID == "LM":
                totDist = sqrt(pow(total_dict["LM"]["LM_Total_X"],2) + pow(total_dict["LM"]["LM_Total_Y"],2))
                total_dict["LM"]["LM_TotDist_cntr_legend"] = totDist
                
            elif leg_ID == "LR":
                totDist = sqrt(pow(total_dict["LR"]["LR_Total_X"],2) + pow(total_dict["LR"]["LR_Total_Y"],2))
                total_dict["LR"]["LR_TotDist_cntr_legend"] = totDist
            
        def AngBodyCntr(leg_ID, total_dict):
            if leg_ID == "RF":
                totAng = degrees(atan2(total_dict["RF"]["RF_Total_Y"], total_dict["RF"]["RF_Total_X"]))
                total_dict["RF"]["RF_AngBdyCntr_X"] = totAng
                
            elif leg_ID =="RM":
                totAng = degrees(atan2(total_dict["RM"]["RM_Total_Y"], total_dict["RM"]["RM_Total_X"]))
                total_dict["RM"]["RM_AngBdyCntr_X"] = totAng
                
            elif leg_ID == "RR":
                totAng = degrees(atan2(total_dict["RR"]["RR_Total_Y"], total_dict["RR"]["RR_Total_X"]))
                total_dict["RR"]["RR_AngBdyCntr_X"] = totAng
                
            elif leg_ID == "LF":
                totAng = degrees(atan2(total_dict["LF"]["LF_Total_Y"], total_dict["LF"]["LF_Total_X"]))
                total_dict["LF"]["LF_AngBdyCntr_X"] = totAng
                
            elif leg_ID == "LM":
                totAng = degrees(atan2(total_dict["LM"]["LM_Total_Y"], total_dict["LM"]["LM_Total_X"]))
                total_dict["LM"]["LM_AngBdyCntr_X"] = totAng
                
            elif leg_ID == "LR":
                totAng = degrees(atan2(total_dict["LR"]["LR_Total_Y"], total_dict["LR"]["LR_Total_X"]))
                total_dict["LR"]["LR_AngBdyCntr_X"] = totAng
                
        Total_X(leg_ID, input_dict, cCoord_dict, coord_dict, total_dict)
        Total_Y(leg_ID, input_dict, cCoord_dict, coord_dict, total_dict)
        
        Total_Z(leg_ID, input_dict, coord_dict, total_dict)
        
        TotDist_cntr_legend(leg_ID, total_dict)
        AngBodyCntr(leg_ID, total_dict)

    
    def RollnPitch_Z(leg_ID, input_dict, total_dict, rp_dict):
        if leg_ID == "RF":
            rp_dict["RF"]["RF_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["RF"]["RF_Total_X"]
            rp_dict["RF"]["RF_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["RF"]["RF_Total_Y"]
            #rp_dict["RF"]["RF_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RF"]["RF_Total_X"]
            #rp_dict["RF"]["RF_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RF"]["RF_Total_Y"]     # nem működött
            
            
        elif leg_ID == "RM":
            rp_dict["RM"]["RM_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["RM"]["RM_Total_X"]
            rp_dict["RM"]["RM_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["RM"]["RM_Total_Y"]
            #rp_dict["RM"]["RM_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RM"]["RM_Total_X"]
            #rp_dict["RM"]["RM_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RM"]["RM_Total_Y"]
            
            """rz = tan(radians(input_dict["ROT_Z"])) * total_dict["RM"]["RM_Total_X"]
            rp_dict["RM"]["RM_Roll_Z"] = rz
            pz = tan(radians(input_dict["ROT_X"])) * total_dict["RM"]["RM_Total_Y"]
            rp_dict["RM"]["RM_Pitch_Z"] = pz"""
        
        elif leg_ID == "RR":
            rp_dict["RR"]["RR_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["RR"]["RR_Total_X"]
            rp_dict["RR"]["RR_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["RR"]["RR_Total_Y"]
            #rp_dict["RR"]["RR_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RR"]["RR_Total_X"]
            #rp_dict["RR"]["RR_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["RR"]["RR_Total_Y"]    
                
            """rz = tan(radians(input_dict["ROT_Z"])) * total_dict["RR"]["RR_Total_X"]
            rp_dict["RR"]["RR_Roll_Z"] = rz
            pz = tan(radians(input_dict["ROT_X"])) * total_dict["RR"]["RR_Total_Y"]
            rp_dict["RR"]["RR_Pitch_Z"] = pz"""
            
        elif leg_ID == "LF":
            rp_dict["LF"]["LF_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["LF"]["LF_Total_X"]
            rp_dict["LF"]["LF_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["LF"]["LF_Total_Y"]
            #rp_dict["LF"]["LF_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LF"]["LF_Total_X"]
            #rp_dict["LF"]["LF_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LF"]["LF_Total_Y"]
            
            """rz = tan(radians(input_dict["ROT_Z"])) * total_dict["LF"]["LF_Total_X"]
            rp_dict["LF"]["LF_Roll_Z"] = rz
            pz = tan(radians(input_dict["ROT_X"])) * total_dict["LF"]["LF_Total_Y"]
            rp_dict["LF"]["LF_Pitch_Z"] = pz"""
            
        elif leg_ID == "LM":
            rp_dict["LM"]["LM_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["LM"]["LM_Total_X"]
            rp_dict["LM"]["LM_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["LM"]["LM_Total_Y"]
            #rp_dict["LM"]["LM_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LM"]["LM_Total_X"]
            #rp_dict["LM"]["LM_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LM"]["LM_Total_Y"]        
                    
            """rz = tan(radians(input_dict["ROT_Z"])) * total_dict["LM"]["LM_Total_X"]
            rp_dict["LM"]["LM_Roll_Z"] = rz
            pz = tan(radians(input_dict["ROT_X"])) * total_dict["LM"]["LM_Total_Y"]
            rp_dict["LM"]["LM_Pitch_Z"] = pz"""
            
        elif leg_ID == "LR":
            rp_dict["LR"]["LR_Roll_Y"] = tan(radians(input_dict["ROT_Y"])) * total_dict["LR"]["LR_Total_X"]
            rp_dict["LR"]["LR_Pitch_X"] = tan(radians(input_dict["ROT_X"])) * total_dict["LR"]["LR_Total_Y"]
            #rp_dict["LR"]["LR_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LR"]["LR_Total_X"]
            #rp_dict["LR"]["LR_Yaw_Z"] = tan(radians(input_dict["ROT_Z"])) * total_dict["LR"]["LR_Total_Y"]
        
            """rz = tan(radians(input_dict["ROT_Z"])) * total_dict["LR"]["LR_Total_X"]
            rp_dict["LR"]["LR_Roll_Z"] = rz
            pz = tan(radians(input_dict["ROT_X"])) * total_dict["LR"]["LR_Total_Y"]
            rp_dict["LR"]["LR_Pitch_Z"] = pz"""
    
            
    def BodyIK(leg_ID, input_dict, total_dict, rp_dict, ik_dict):
        if leg_ID == "RF":
            ik_x = cos(radians(total_dict["RF"]["RF_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RF"]["RF_TotDist_cntr_legend"] - total_dict["RF"]["RF_Total_X"]    # ROT_Y kicesrélve ROT_Z-re
            ik_dict["RF"]["RF_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["RF"]["RF_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RF"]["RF_TotDist_cntr_legend"] - total_dict["RF"]["RF_Total_Y"]
            ik_dict["RF"]["RF_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["RF"]["RF_Roll_Y"] + rp_dict["RF"]["RF_Pitch_X"] + rp_dict["RF"]["RF_Yaw_Z"]    # modification on 2020. April 12
            ik_z = rp_dict["RF"]["RF_Roll_Y"] + rp_dict["RF"]["RF_Pitch_X"]
            ik_dict["RF"]["RF_BodyIK_Z"] = ik_z
            
        elif leg_ID == "RM":
            ik_x = cos(radians(total_dict["RM"]["RM_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RM"]["RM_TotDist_cntr_legend"] - total_dict["RM"]["RM_Total_X"]
            ik_dict["RM"]["RM_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["RM"]["RM_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RM"]["RM_TotDist_cntr_legend"] - total_dict["RM"]["RM_Total_Y"]
            ik_dict["RM"]["RM_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["RM"]["RM_Roll_Y"] + rp_dict["RM"]["RM_Pitch_X"] + rp_dict["RM"]["RM_Yaw_Z"]
            ik_z = rp_dict["RM"]["RM_Roll_Y"] + rp_dict["RM"]["RM_Pitch_X"]
            ik_dict["RM"]["RM_BodyIK_Z"] = ik_z
            
        elif leg_ID == "RR":
            ik_x = cos(radians(total_dict["RR"]["RR_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RR"]["RR_TotDist_cntr_legend"] - total_dict["RR"]["RR_Total_X"]
            ik_dict["RR"]["RR_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["RR"]["RR_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["RR"]["RR_TotDist_cntr_legend"] - total_dict["RR"]["RR_Total_Y"]
            ik_dict["RR"]["RR_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["RR"]["RR_Roll_Y"] + rp_dict["RR"]["RR_Pitch_X"] + rp_dict["RR"]["RR_Yaw_Z"]
            ik_z = rp_dict["RR"]["RR_Roll_Y"] + rp_dict["RR"]["RR_Pitch_X"]
            ik_dict["RR"]["RR_BodyIK_Z"] = ik_z
            
        elif leg_ID == "LF":
            ik_x = cos(radians(total_dict["LF"]["LF_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LF"]["LF_TotDist_cntr_legend"] - total_dict["LF"]["LF_Total_X"]
            ik_dict["LF"]["LF_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["LF"]["LF_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LF"]["LF_TotDist_cntr_legend"] - total_dict["LF"]["LF_Total_Y"]
            ik_dict["LF"]["LF_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["LF"]["LF_Roll_Y"] + rp_dict["LF"]["LF_Pitch_X"] + rp_dict["LF"]["LF_Yaw_Z"]
            ik_z = rp_dict["LF"]["LF_Roll_Y"] + rp_dict["LF"]["LF_Pitch_X"]
            ik_dict["LF"]["LF_BodyIK_Z"] = ik_z
            
        elif leg_ID == "LM":
            ik_x = cos(radians(total_dict["LM"]["LM_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LM"]["LM_TotDist_cntr_legend"] - total_dict["LM"]["LM_Total_X"]
            ik_dict["LM"]["LM_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["LM"]["LM_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LM"]["LM_TotDist_cntr_legend"] - total_dict["LM"]["LM_Total_Y"]
            ik_dict["LM"]["LM_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["LM"]["LM_Roll_Y"] + rp_dict["LM"]["LM_Pitch_X"] + rp_dict["LM"]["LM_Yaw_Z"]
            ik_z = rp_dict["LM"]["LM_Roll_Y"] + rp_dict["LM"]["LM_Pitch_X"]
            ik_dict["LM"]["LM_BodyIK_Z"] = ik_z
            
        elif leg_ID == "LR":
            ik_x = cos(radians(total_dict["LR"]["LR_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LR"]["LR_TotDist_cntr_legend"] - total_dict["LR"]["LR_Total_X"]
            ik_dict["LR"]["LR_BodyIK_X"] = ik_x
            ik_y = sin(radians(total_dict["LR"]["LR_AngBdyCntr_X"] + input_dict["ROT_Z"])) * total_dict["LR"]["LR_TotDist_cntr_legend"] - total_dict["LR"]["LR_Total_Y"]
            ik_dict["LR"]["LR_BodyIK_Y"] = ik_y
            #ik_z = rp_dict["LR"]["LR_Roll_Y"] + rp_dict["LR"]["LR_Pitch_X"] + rp_dict["LR"]["LR_Yaw_Z"]
            ik_z = rp_dict["LR"]["LR_Roll_Y"] + rp_dict["LR"]["LR_Pitch_X"]
            ik_dict["LR"]["LR_BodyIK_Z"] = ik_z
        
        
    def LegNewPos(leg_ID, input_dict, coord_dict, ik_dict, newpos_dict):
        if leg_ID == "RF":
            np_x = coord_dict["RF"]["RF_FeetPos_X"] + input_dict["POS_X"] + ik_dict["RF"]["RF_BodyIK_X"]
            newpos_dict["RF"]["RF_NewPos_X"] = np_x
            np_y = coord_dict["RF"]["RF_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["RF"]["RF_BodyIK_Y"]
            newpos_dict["RF"]["RF_NewPos_Y"] = np_y
            np_z =  coord_dict["RF"]["RF_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["RF"]["RF_BodyIK_Z"]       
            newpos_dict["RF"]["RF_NewPos_Z"] = np_z
            
        elif leg_ID == "RM":
            np_x = coord_dict["RM"]["RM_FeetPos_X"] + input_dict["POS_X"] + ik_dict["RM"]["RM_BodyIK_X"]
            newpos_dict["RM"]["RM_NewPos_X"] = np_x
            np_y = coord_dict["RM"]["RM_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["RM"]["RM_BodyIK_Y"]
            newpos_dict["RM"]["RM_NewPos_Y"] = np_y
            np_z =  coord_dict["RM"]["RM_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["RM"]["RM_BodyIK_Z"]       
            newpos_dict["RM"]["RM_NewPos_Z"] = np_z
            
        elif leg_ID == "RR":
            np_x = coord_dict["RR"]["RR_FeetPos_X"] + input_dict["POS_X"] + ik_dict["RR"]["RR_BodyIK_X"]
            newpos_dict["RR"]["RR_NewPos_X"] = np_x
            np_y = coord_dict["RR"]["RR_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["RR"]["RR_BodyIK_Y"]
            newpos_dict["RR"]["RR_NewPos_Y"] = np_y
            np_z =  coord_dict["RR"]["RR_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["RR"]["RR_BodyIK_Z"]       
            newpos_dict["RR"]["RR_NewPos_Z"] = np_z
            
        elif leg_ID == "LF":
            np_x = coord_dict["LF"]["LF_FeetPos_X"] + input_dict["POS_X"] + ik_dict["LF"]["LF_BodyIK_X"]
            newpos_dict["LF"]["LF_NewPos_X"] = np_x
            np_y = coord_dict["LF"]["LF_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["LF"]["LF_BodyIK_Y"]
            newpos_dict["LF"]["LF_NewPos_Y"] = np_y
            np_z =  coord_dict["LF"]["LF_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["LF"]["LF_BodyIK_Z"]       
            newpos_dict["LF"]["LF_NewPos_Z"] = np_z
            
        elif leg_ID == "LM":
            np_x = coord_dict["LM"]["LM_FeetPos_X"] + input_dict["POS_X"] + ik_dict["LM"]["LM_BodyIK_X"]
            newpos_dict["LM"]["LM_NewPos_X"] = np_x
            np_y = coord_dict["LM"]["LM_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["LM"]["LM_BodyIK_Y"]
            newpos_dict["LM"]["LM_NewPos_Y"] = np_y
            np_z =  coord_dict["LM"]["LM_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["LM"]["LM_BodyIK_Z"]       
            newpos_dict["LM"]["LM_NewPos_Z"] = np_z
            
        elif leg_ID == "LR":
            np_x = coord_dict["LR"]["LR_FeetPos_X"] + input_dict["POS_X"] + ik_dict["LR"]["LR_BodyIK_X"]
            newpos_dict["LR"]["LR_NewPos_X"] = np_x
            np_y = coord_dict["LR"]["LR_FeetPos_Y"] + input_dict["POS_Y"] + ik_dict["LR"]["LR_BodyIK_Y"]
            newpos_dict["LR"]["LR_NewPos_Y"] = np_y
            np_z =  coord_dict["LR"]["LR_FeetPos_Z"] + input_dict["POS_Z"] + ik_dict["LR"]["LR_BodyIK_Z"]       
            newpos_dict["LR"]["LR_NewPos_Z"] = np_z
            
            
    def LegAuxDists(leg_ID, np_dict, const_dict, aux_dict):
        if leg_ID == "RF":
            dcle = sqrt(pow(np_dict["RF"]["RF_NewPos_X"], 2) + pow(np_dict["RF"]["RF_NewPos_Y"], 2))
            aux_dict["RF"]["RF_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["RF"]["RF_NewPos_Z"], 2))
            aux_dict["RF"]["RF_L"] = l
                        
        elif leg_ID == "RM":
            dcle = sqrt(pow(np_dict["RM"]["RM_NewPos_X"], 2) + pow(np_dict["RM"]["RM_NewPos_Y"], 2))
            aux_dict["RM"]["RM_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["RM"]["RM_NewPos_Z"], 2))
            aux_dict["RM"]["RM_L"] = l
            
        elif leg_ID == "RR":
            dcle = sqrt(pow(np_dict["RR"]["RR_NewPos_X"], 2) + pow(np_dict["RR"]["RR_NewPos_Y"], 2))
            aux_dict["RR"]["RR_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["RR"]["RR_NewPos_Z"], 2))
            aux_dict["RR"]["RR_L"] = l
            
        elif leg_ID == "LF":
            dcle = sqrt(pow(np_dict["LF"]["LF_NewPos_X"], 2) + pow(np_dict["LF"]["LF_NewPos_Y"], 2))
            aux_dict["LF"]["LF_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["LF"]["LF_NewPos_Z"], 2))
            aux_dict["LF"]["LF_L"] = l
            
        elif leg_ID == "LM":
            dcle = sqrt(pow(np_dict["LM"]["LM_NewPos_X"], 2) + pow(np_dict["LM"]["LM_NewPos_Y"], 2))
            aux_dict["LM"]["LM_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["LM"]["LM_NewPos_Z"], 2))
            aux_dict["LM"]["LM_L"] = l
            
        elif leg_ID == "LR":
            dcle = sqrt(pow(np_dict["LR"]["LR_NewPos_X"], 2) + pow(np_dict["LR"]["LR_NewPos_Y"], 2))
            aux_dict["LR"]["LR_DistCoxaLegend"] = dcle
            l = sqrt(pow((dcle - const_dict["lCoxa"]), 2) + pow(np_dict["LR"]["LR_NewPos_Z"], 2))
            aux_dict["LR"]["LR_L"] = l
        
        
    def AngsFromTriangles(leg_ID, aux_dist_dict, np_dict, const_dict, trgang_dict):
        def PlausibleCheck(expr):
            if expr > 1:
                expr = 1
                print ("IK_CALC: WARNING: MathLimit acos reached!")
                return expr
                
            elif expr < -1:
                expr = -1
                print ("IK_CALC: WARNING: MathLimit acos reached!")
                return expr
            
            else:
                return expr
                
            
        if leg_ID == "RF":
            a1 = degrees(atan((aux_dist_dict["RF"]["RF_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["RF"]["RF_NewPos_Z"]))
            trgang_dict["RF"]["RF_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["RF"]["RF_L"], 2)) / (-2 * aux_dist_dict["RF"]["RF_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["RF"]["RF_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["RF"]["RF_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["RF"]["RF_Beta"] = b
            
        elif leg_ID == "RM":    
            a1 = degrees(atan((aux_dist_dict["RM"]["RM_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["RM"]["RM_NewPos_Z"]))
            trgang_dict["RM"]["RM_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["RM"]["RM_L"], 2)) / (-2 * aux_dist_dict["RM"]["RM_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["RM"]["RM_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["RM"]["RM_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["RM"]["RM_Beta"] = b
        
        elif leg_ID == "RR":
            a1 = degrees(atan((aux_dist_dict["RR"]["RR_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["RR"]["RR_NewPos_Z"]))
            trgang_dict["RR"]["RR_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["RR"]["RR_L"], 2)) / (-2 * aux_dist_dict["RR"]["RR_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["RR"]["RR_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["RR"]["RR_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["RR"]["RR_Beta"] = b
        
        elif leg_ID == "LF":
            a1 = degrees(atan((aux_dist_dict["LF"]["LF_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["LF"]["LF_NewPos_Z"]))
            trgang_dict["LF"]["LF_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["LF"]["LF_L"], 2)) / (-2 * aux_dist_dict["LF"]["LF_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["LF"]["LF_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["LF"]["LF_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["LF"]["LF_Beta"] = b
        
        elif leg_ID == "LM":
            a1 = degrees(atan((aux_dist_dict["LM"]["LM_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["LM"]["LM_NewPos_Z"]))
            trgang_dict["LM"]["LM_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["LM"]["LM_L"], 2)) / (-2 * aux_dist_dict["LM"]["LM_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["LM"]["LM_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["LM"]["LM_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["LM"]["LM_Beta"] = b
        
        elif leg_ID == "LR":
            a1 = degrees(atan((aux_dist_dict["LR"]["LR_DistCoxaLegend"] - const_dict["lCoxa"]) / np_dict["LR"]["LR_NewPos_Z"]))
            trgang_dict["LR"]["LR_Alpha1"] = a1
            
            expr_1 = ((pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2) - pow(aux_dist_dict["LR"]["LR_L"], 2)) / (-2 * aux_dist_dict["LR"]["LR_L"] * const_dict["lFemur"]))
            a2 = degrees(acos(PlausibleCheck(expr_1)))
            trgang_dict["LR"]["LR_Alpha2"] = a2
            
            expr_2 = ((pow(aux_dist_dict["LR"]["LR_L"], 2) - pow(const_dict["lTibia"], 2) - pow(const_dict["lFemur"], 2)) / (-2 * const_dict["lFemur"] * const_dict["lTibia"]))
            b = degrees(acos(PlausibleCheck(expr_2)))
            trgang_dict["LR"]["LR_Beta"] = b
            
    
    def LegRawAngles(leg_ID, newpos_dict, trgang_dict, rawang_dict):
        if leg_ID == "RF":
            rawang_dict["RF"]["RF_CoxaAng"]  = 90.0 - degrees(atan2(newpos_dict["RF"]["RF_NewPos_Y"], newpos_dict["RF"]["RF_NewPos_X"]))
            rawang_dict["RF"]["RF_FemurAng"] = trgang_dict["RF"]["RF_Alpha1"] + trgang_dict["RF"]["RF_Alpha2"]
            rawang_dict["RF"]["RF_TibiaAng"] = trgang_dict["RF"]["RF_Beta"]
            
        elif leg_ID == "RM":
            rawang_dict["RM"]["RM_CoxaAng"]  = degrees(atan2(newpos_dict["RM"]["RM_NewPos_Y"], newpos_dict["RM"]["RM_NewPos_X"]))
            rawang_dict["RM"]["RM_FemurAng"] = trgang_dict["RM"]["RM_Alpha1"] + trgang_dict["RM"]["RM_Alpha2"]
            rawang_dict["RM"]["RM_TibiaAng"] = trgang_dict["RM"]["RM_Beta"]
        
        elif leg_ID == "RR":
            rawang_dict["RR"]["RR_CoxaAng"]  = -90.0 - degrees(atan2(newpos_dict["RR"]["RR_NewPos_Y"], newpos_dict["RR"]["RR_NewPos_X"]))
            rawang_dict["RR"]["RR_FemurAng"] = trgang_dict["RR"]["RR_Alpha1"] + trgang_dict["RR"]["RR_Alpha2"]
            rawang_dict["RR"]["RR_TibiaAng"] = trgang_dict["RR"]["RR_Beta"]
        
        elif leg_ID == "LF":
            rawang_dict["LF"]["LF_CoxaAng"]  = 90.0 - degrees(atan2(newpos_dict["LF"]["LF_NewPos_Y"], newpos_dict["LF"]["LF_NewPos_X"]))
            rawang_dict["LF"]["LF_FemurAng"] = trgang_dict["LF"]["LF_Alpha1"] + trgang_dict["LF"]["LF_Alpha2"]
            rawang_dict["LF"]["LF_TibiaAng"] = trgang_dict["LF"]["LF_Beta"]
        
        elif leg_ID == "LM":
            rawang_dict["LM"]["LM_CoxaAng"]  = degrees(atan2(newpos_dict["LM"]["LM_NewPos_Y"], newpos_dict["LM"]["LM_NewPos_X"]))
            rawang_dict["LM"]["LM_FemurAng"] = trgang_dict["LM"]["LM_Alpha1"] + trgang_dict["LM"]["LM_Alpha2"]
            rawang_dict["LM"]["LM_TibiaAng"] = trgang_dict["LM"]["LM_Beta"]
            
        elif leg_ID == "LR":
            rawang_dict["LR"]["LR_CoxaAng"]  = -90.0 - degrees(atan2(newpos_dict["LR"]["LR_NewPos_Y"], newpos_dict["LR"]["LR_NewPos_X"]))
            rawang_dict["LR"]["LR_FemurAng"] = trgang_dict["LR"]["LR_Alpha1"] + trgang_dict["LR"]["LR_Alpha2"]
            rawang_dict["LR"]["LR_TibiaAng"] = trgang_dict["LR"]["LR_Beta"]
        
        
    def LegRawAngRecalc(leg_ID, rawang_dict, recalc_dict):
        if leg_ID == "RF":
            recalc_dict["RF"]["RF_CoxaAng"] = 180.0 - (38.0 + rawang_dict["RF"]["RF_CoxaAng"])
            recalc_dict["RF"]["RF_FemurAng"] = rawang_dict["RF"]["RF_FemurAng"]
            recalc_dict["RF"]["RF_TibiaAng"] = 180.0 - rawang_dict["RF"]["RF_TibiaAng"]
            
            
        elif leg_ID == "RM":
            recalc_dict["RM"]["RM_CoxaAng"] = 90.0 + rawang_dict["RM"]["RM_CoxaAng"]
            recalc_dict["RM"]["RM_FemurAng"] = rawang_dict["RM"]["RM_FemurAng"]
            recalc_dict["RM"]["RM_TibiaAng"] = 180 - rawang_dict["RM"]["RM_TibiaAng"]
        
        elif leg_ID == "RR":
            recalc_dict["RR"]["RR_CoxaAng"] = (-38.0 + rawang_dict["RR"]["RR_CoxaAng"]) * -1
            recalc_dict["RR"]["RR_FemurAng"] = rawang_dict["RR"]["RR_FemurAng"]
            recalc_dict["RR"]["RR_TibiaAng"] = 180.0 - rawang_dict["RR"]["RR_TibiaAng"]
        
        elif leg_ID == "LF":
            recalc_dict["LF"]["LF_CoxaAng"] = (-38.0 + rawang_dict["LF"]["LF_CoxaAng"]) * -1
            recalc_dict["LF"]["LF_FemurAng"] = 180.0 - rawang_dict["LF"]["LF_FemurAng"]
            recalc_dict["LF"]["LF_TibiaAng"] = rawang_dict["LF"]["LF_TibiaAng"]
        
        elif leg_ID == "LM":
            if rawang_dict["LM"]["LM_CoxaAng"] >= 0:
                recalc_dict["LM"]["LM_CoxaAng"] = abs(180 - 90 - abs(rawang_dict["LM"]["LM_CoxaAng"]))
            elif rawang_dict["LM"]["LM_CoxaAng"] < 0:
                recalc_dict["LM"]["LM_CoxaAng"] = 180 - abs(180 -90 - abs(rawang_dict["LM"]["LM_CoxaAng"]))
            
            #recalc_dict["LM"]["LM_CoxaAng"] =  180.0 - abs(180 - 90 - abs(rawang_dict["LM"]["LM_CoxaAng"])) # Ha POS_Y=>0 akkor abs(180-90-abs(LM_CoxaAng)), ha POS_Y<= akkor 180-abs(180-90-abs(LM_CoxaAng)) 
            #recalc_dict["LM"]["LM_CoxaAng"] =  180.0 - (90.0 + rawang_dict["LM"]["LM_CoxaAng"])
            #print recalc_dict["LM"]["LM_CoxaAng"]
            recalc_dict["LM"]["LM_FemurAng"] = 180.0 - rawang_dict["LM"]["LM_FemurAng"]
            recalc_dict["LM"]["LM_TibiaAng"] = rawang_dict["LM"]["LM_TibiaAng"]
        
        elif leg_ID == "LR":
            recalc_dict["LR"]["LR_CoxaAng"] = 180.0 - (38.0 + rawang_dict["LR"]["LR_CoxaAng"])
            recalc_dict["LR"]["LR_FemurAng"] = 180.0 - rawang_dict["LR"]["LR_FemurAng"]
            recalc_dict["LR"]["LR_TibiaAng"] = rawang_dict["LR"]["LR_TibiaAng"]
        
    def FinalAngToMs(leg_ID, recalc_dict, output_dict):
        def ConvAngToMs (ang):
            srvo_pos = (((2500.0-500.0) / 180.0) * ang) + 500.0
            if srvo_pos > 2500:
                srvo_pos = 2500.0
                return srvo_pos
                
            elif srvo_pos < 500:
                srvo_pos = 500.0
                return srvo_pos
                
            else:
                return srvo_pos
    
        def ConvAngToMsJX (ang):
            srvo_pos = (((500.0-2500.0) / 180.0) * ang) + 2500
            if srvo_pos > 2500:
                srvo_pos = 2500.0
                return srvo_pos
                
            elif srvo_pos < 500:
                srvo_pos = 500.0
                return srvo_pos
                
            else:
                return srvo_pos

        if leg_ID == "RF":
            output_dict["RF"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["RF"]["RF_CoxaAng"])) + calibr_dict["RF"]["pos_coxa"])
            output_dict["RF"]["pos_femur"] = int(round(ConvAngToMsJX(recalc_dict["RF"]["RF_FemurAng"])) + calibr_dict["RF"]["pos_femur"])
            output_dict["RF"]["pos_tibia"] = int(round(ConvAngToMsJX(recalc_dict["RF"]["RF_TibiaAng"])) + calibr_dict["RF"]["pos_tibia"])
            
        elif leg_ID == "RM":
            output_dict["RM"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["RM"]["RM_CoxaAng"])) + calibr_dict["RM"]["pos_coxa"])
            output_dict["RM"]["pos_femur"] = int(round(ConvAngToMs(recalc_dict["RM"]["RM_FemurAng"])) + calibr_dict["RM"]["pos_femur"])
            output_dict["RM"]["pos_tibia"] = int(round(ConvAngToMs(recalc_dict["RM"]["RM_TibiaAng"])) + calibr_dict["RM"]["pos_tibia"])
            
        elif leg_ID == "RR":
            output_dict["RR"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["RR"]["RR_CoxaAng"])) + calibr_dict["RR"]["pos_coxa"])
            output_dict["RR"]["pos_femur"] = int(round(ConvAngToMs(recalc_dict["RR"]["RR_FemurAng"])) + calibr_dict["RR"]["pos_femur"])
            output_dict["RR"]["pos_tibia"] = int(round(ConvAngToMs(recalc_dict["RR"]["RR_TibiaAng"])) + calibr_dict["RR"]["pos_tibia"])
        
        elif leg_ID == "LF":
            output_dict["LF"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["LF"]["LF_CoxaAng"])) + calibr_dict["LF"]["pos_coxa"])
            output_dict["LF"]["pos_femur"] = int(round(ConvAngToMsJX(recalc_dict["LF"]["LF_FemurAng"])) + calibr_dict["LF"]["pos_femur"])
            output_dict["LF"]["pos_tibia"] = int(round(ConvAngToMsJX(recalc_dict["LF"]["LF_TibiaAng"])) + calibr_dict["LF"]["pos_tibia"])
            
        elif leg_ID == "LM":
            output_dict["LM"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["LM"]["LM_CoxaAng"])) + calibr_dict["LM"]["pos_coxa"])
            output_dict["LM"]["pos_femur"] = int(round(ConvAngToMs(recalc_dict["LM"]["LM_FemurAng"])) + calibr_dict["LM"]["pos_femur"])
            output_dict["LM"]["pos_tibia"] = int(round(ConvAngToMs(recalc_dict["LM"]["LM_TibiaAng"])) + calibr_dict["LM"]["pos_tibia"])
        
        elif leg_ID == "LR":
            output_dict["LR"]["pos_coxa"] = int(round(ConvAngToMs(recalc_dict["LR"]["LR_CoxaAng"])) + calibr_dict["LR"]["pos_coxa"])
            output_dict["LR"]["pos_femur"] = int(round(ConvAngToMs(recalc_dict["LR"]["LR_FemurAng"])) + calibr_dict["LR"]["pos_femur"])
            output_dict["LR"]["pos_tibia"] = int(round(ConvAngToMs(recalc_dict["LR"]["LR_TibiaAng"])) + calibr_dict["LR"]["pos_tibia"])
    
    
    LegEndPoint(leg_ID, ConstantVal, input_dict, FeetPosVal)                     #testing with input_dict, before input_dict there was IK_in
    LegTotal(leg_ID, input_dict, CoxaCoord, FeetPosVal, LegTotalVal)             #testing with input_dict, before input_dict there was IK_in
    RollnPitch_Z(leg_ID, input_dict, LegTotalVal, RollPitchVal)                  #testing with input_dict, before input_dict there was IK_in
    BodyIK(leg_ID, input_dict, LegTotalVal, RollPitchVal, BodyIKVal)             #testing with input_dict, before input_dict there was IK_in
    LegNewPos(leg_ID, input_dict, FeetPosVal, BodyIKVal, NewPos)                 #testing with input_dict, before input_dict there was IK_in
    LegAuxDists(leg_ID, NewPos, ConstantVal, LegAuxVal)
    AngsFromTriangles(leg_ID, LegAuxVal, NewPos, ConstantVal, TrgAngVal)
    LegRawAngles(leg_ID, NewPos, TrgAngVal, RawAngVal)
    LegRawAngRecalc(leg_ID, RawAngVal, RawAngRecalc)
    FinalAngToMs(leg_ID, RawAngRecalc, output_dict)
    
    """
    if leg_ID == "RF":
        print RawAngRecalc["RF"]
    elif leg_ID == "RM":
        print RawAngRecalc["RM"]
    elif leg_ID =="RR":
        print RawAngRecalc["RR"]
    elif leg_ID == "LF":
        print RawAngRecalc["LF"]
    elif leg_ID == "LM":
        print RawAngRecalc["LM"]
    elif leg_ID == "LR":
        print RawAngRecalc["LR"]
    """
    
def IK_Diag(output_dict):
    print ("RF")
    print ("Coxa pos.: " + str(output_dict["RF"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["RF"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["RF"]["pos_tibia"]) + "\n")
    
    print ("RM")
    print ("Coxa pos.: " + str(output_dict["RM"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["RM"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["RM"]["pos_tibia"]) + "\n")
    
    print ("RR")
    print ("Coxa pos.: " + str(output_dict["RR"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["RR"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["RR"]["pos_tibia"]) + "\n")
    
    print ("LF")
    print ("Coxa pos.: " + str(output_dict["LF"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["LF"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["LF"]["pos_tibia"]) + "\n")
    
    print ("LM")
    print ("Coxa pos.: " + str(output_dict["LM"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["LM"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["LM"]["pos_tibia"]) + "\n")
    
    print ("LR")
    print ("Coxa pos.: " + str(output_dict["LR"]["pos_coxa"]))
    print ("Femur pos.: " + str(output_dict["LR"]["pos_femur"]))
    print ("Tibia pos.: " + str(output_dict["LR"]["pos_tibia"]) + "\n")
    
    
def IK_SixLeg():
    IK("RF", IK_in, ConstantVal, SrvoCalibrVal, IK_out)
    IK("RM", IK_in, ConstantVal, SrvoCalibrVal, IK_out)
    IK("RR", IK_in, ConstantVal, SrvoCalibrVal, IK_out)
    IK("LF", IK_in, ConstantVal, SrvoCalibrVal, IK_out)
    IK("LM", IK_in, ConstantVal, SrvoCalibrVal, IK_out)
    IK("LR", IK_in, ConstantVal, SrvoCalibrVal, IK_out)


def IK_Tripod_A(mode):
    if mode == "support":
        IK("RF", IK_in, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        IK("LM", IK_in, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        IK("RR", IK_in, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        #print TripodA_MoveTable
    elif mode == "swing":
        IK("RF", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        IK("LM", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        IK("RR", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodA_MoveTable)
        
        
def IK_Tripod_B(mode):
    if mode == "support":
        IK("LF", IK_in, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)
        IK("RM", IK_in, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)
        IK("LR", IK_in, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)

    elif mode == "swing":
        IK("LF", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)
        IK("RM", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)
        IK("LR", IK_in_for_Swing, ConstantVal, SrvoCalibrVal, TripodB_MoveTable)

        
    
def CalcWalkVector():
    Vector = sqrt(pow(IK_in["POS_X"],2) + pow(IK_in["POS_Y"],2))
    if Vector < 0.14:
        Vector = 0
        return Vector
    else:
        return Vector


def CalcStepTime(vector):
    """MAX movetime = 3000ms, MIN movetime = 750ms
    MAX vector = 1,41, MIN vector = 0,1"""
    Time = ((750 - 3000) * ((vector - 0.1) / (1.41 - 0.1))) + 3000
    return Time
    

def IK_Calc_SwingLegs(aux_coord, aux_val, direction):
        if direction == "up":
            if aux_val["dist_to_grnd"] - aux_val["lift_value"] > 120:
                aux_coord["POS_Z"] = aux_coord["POS_Z"] - aux_val["lift_value"]
            elif aux_val["dist_to_grnd"] - aux_val["lift_value"] < 120:
                aux_val["diff"] = aux_val["dist_to_grnd"] - aux_val["lift_value"]
                aux_coord["POS_Z"] = aux_coord["POS_Z"] - aux_val["diff"]
                aux_val["recoveryReq"] = True
        elif direction == "down":
            if aux_val["recoveryReq"] == True:
                aux_coord["POS_Z"] + aux_val["diff"]
            else:
                aux_coord["POS_Z"] = aux_coord["POS_Z"] + aux_val["lift_value"]


def CalcHeadPos(input, calibrationVal, output):
    def AngToMs(ang):
        srvo_pos = (((2500.0-500.0) / 180.0) * ang) + 500.0
        if srvo_pos > 2500:
            srvo_pos = 2500.0
            return srvo_pos
        elif srvo_pos < 500:
            srvo_pos = 500.0
            return srvo_pos
        else:
            return srvo_pos

    input["headBow_mod"] = input["headBow_def"] + input["headBow_diff"]
    input["headTwist_mod"] = input["headTwist_def"] + input["headTwist_diff"]
    input["headSide_mod"] = input["headSide_def"] + input["headSide_diff"]

    output["pos_headBow"] = int(round(AngToMs(input["headBow_mod"]))) + calibrationVal["pos_headBow"]
    output["pos_headTwist"] = int(round(AngToMs(input["headTwist_mod"]))) + calibrationVal["pos_headTwist"]
    output["pos_headSide"] = int(round(AngToMs(input["headSide_mod"]))) + calibrationVal["pos_headSide"]

    
#IK_Tripod_B("swing")
#IK_SixLeg()
#IK_Diag(IK_out)

