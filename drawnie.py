# -*- coding: utf-8 -*-
#drawnie.py
#author: Drawnie team CRI
#date : november 2019
#version : V1.0

import math
import tkinter
import time
import serial
from datetime import datetime
import numpy as np

#maybe not necessary if we want to make automation on it
LG_SURF = 1000 #mm distance between the 2 steppers
HEIGHT_SURF = 1000 #mm height surface
delay_motor = 0.08 #seconde as delay for sending instructions to arduino

'''
                Our coordinate system is :

                (0,HEIGHT_SURF)....(LG_SURF,HEIGHT_SURF)
                .                   .
                .                   .
                .                   .
                (0,0)..............(LG_SURF,0)
                Origin point is in the left corner
                We start the program with the calibration in the middle of the surface :
                    Origin point is (x=LG_SURF/2, y=HEIGHT_SURF)
                    
        Drawnie is composed of 3 motors :
        Motor 0 : left stepper motor
        Motor 1 : right stepper motor
        Motor 2 : servo motor, pen holder
   
'''

'''
    class Drawbot() is the class who does the mathematical of the drawbot system
'''
class Drawbot (object):
    def __init__(self):
        '''
            Size in mm of the drawing surface
        '''
        self.mmWidth = LG_SURF
        self.mmHeight = HEIGHT_SURF

        # Number of thread by revolutions per motor
        self.motorStepsPerRev = 200
        self.mmPerRev = 12 * math.pi
        print("mmPerRev : ", self.mmPerRev)

        self.deltamin = self.mmPerRev / self.motorStepsPerRev
        self.deltastep = 0.05 #smaller than delta in purpose to gain in precision

        #number of mm by Steps
        self.mmPerStep = self.mmPerRev / self.motorStepsPerRev
        print("mmPerStep : ", self.mmPerStep)

        '''
            Size in steps of the drawing surface
        '''
        self.stepsWidth = self.mmWidth / self.mmPerStep
        self.stepsHeight = self.mmHeight / self.mmPerStep
        print("stepsWidth", self.stepsWidth)
        print("stepsHeight", self.stepsHeight)

        '''
            Position of the pen holder
            originX is the x coordinate for the center
            originY is the y coordinate for the center
        '''
        self.originX = self.mmWidth/2
        self.originY = self.mmHeight/2

        '''
            Position of the pen holder
            currentX is the x coordinate
            currentY is the y coordinate
        '''
        self.currentX = self.originX
        self.currentY = self.originY

        '''
            marginX is the margin where the penholder can't go in the axe X
            marginY is the margin where the penholder can't go in the axe Y
        '''
        self.marginX = 150
        self.marginY = 150

        #opening a connexion with Arduino on the port /dev/ttyACM0 something
        self.a = serial.Serial("/dev/ttyACM0", 9600, timeout=0)

    '''
        drawStraightLine(X1, Y1, targetX,targetY) : draw a line from (X1,Y1) to (targetX,targetY)
            X1 : x coordinate of the line origin
            Y1 : y coordinate of the line origin
            target X : x coordinate of the end of the line
            target Y : y coordinate of the end of the line
     '''
    def drawStraightline (self, X1, Y1, targetX, targetY):
        indic_drawing = False
        while indic_drawing == False:
            if (X1 != self.currentX and Y1 != self.currentY):
                #send instruction to the servomotor (motor 2) to make the pen up
                #MOVE
                self.write_file("2,0\0")
                self.a.write("2,0\0".encode())
                self.motors_move(self.currentX, self.currentY, X1, Y1)
                time.sleep(delay_motor)
            else:
                #send instruction to the servomotor (motor 2) to make the pen down
                #WRITE
                self.write_file("2,1\0")
                self.a.write("2,1\0".encode())
                self.motors_move(X1, Y1, targetX, targetY)
                time.sleep(delay_motor)
                indic_drawing = True

    '''
        reinit_drawing() : put the cursor at the orgin point
    '''
    def reinit_drawing (self):
        # send instruction to the servomotor (motor 2) to make up the pen
        # MOVE
        self.write_file("2,0\0")
        self.a.write("2,0\0".encode())
        self.motors_move(self.currentX, self.currentY, self.originX, self.originY)
        time.sleep(delay_motor)

    '''
        drawSquare(coordX, coordY, length)
            coordX = x coordinate for the origin point of the square
            coordY = y coordinate for the origin point of the square
            length of the square in mm
     '''
    def drawSquare (self, coordX, coordY, length):
        squareX = []
        squareY = []
        #coordinate 0
        squareX.append(coordX)
        squareY.append(coordY)
        # coordinate 1
        squareX.append(coordX+length)
        squareY.append(coordY)
        # coordinate 2
        squareX.append(coordX+length)
        squareY.append(coordY-length)
        # coordinate 3
        squareX.append(coordX)
        squareY.append(coordY-length)

        cpt_points = 0
        while cpt_points < 4:
            #last point
            if cpt_points == 3:
                self.drawStraightline(squareX[cpt_points], squareY[cpt_points],  squareX[0],squareY[0])
            else :
                self.drawStraightline(squareX[cpt_points],squareY[cpt_points],squareX[cpt_points+1],squareY[cpt_points+1])
            cpt_points +=1

    '''
        convertstepsTomm (distance) : conversion of a steps distance to a distance in mm
        distance : distance to convert
    '''
    def convertstepsTomm (self, distance):
        return (distance * self.mmPerStep)

    '''
        convertmmTosteps (distance) : conversion of distance in a mm to a distance in steps
        distance : distance to convert
    '''
    def convertmmTosteps (self, distance):
        return (distance / self.mmPerStep)

    '''
        looknbStep(L1, L2) : calculate the number of revolutions to send to the motor 
        comparing the lengths L1 and L2
        L1 : first length to compare
        L2 : second length to compare
     '''
    def looknbStep(self, L1, L2):
        if L1>L2:
            inter= round(L1 - L2)
        else:
            inter = round(L2 - L1)
        if inter == 0: #for example, L1 = 24,015 and L2 = 24,5, the round would be 0 but the motor has to move 1 step
            inter = 1
        return inter

    '''
    write_file() is a function for writing in a external text file
    mvt_m : string to write in the file
    '''
    def write_file(self, mvt_m):
        path_m = "./exemples_motors_move.txt"
        file_m = open(path_m, "a")
        mvt_m = datetime.now().strftime("%H:%M:%S %d/%m/%y : ") + mvt_m + '\n'
        file_m.write(mvt_m)
        file_m.close()

    '''
        motors_move(X1, Y1, targetX,targetY) : make the motor moves from (X1,Y1) to (targetX,targetY)
        Inverse model : we know the target
        Always verify to that x belongs to [0 ; mmWidth] and y belongs to [0 ; mmHeight] in mm, we have to convert it in steps
        In a first time, we calculate angles teta1 and teta2. These are the angles between the motors and the rubber
        Second, we calculate the lengths L1 et L2 which are the final lengths that needed for the motors
        L1 et L2 must belong to [0; sqrt(pow(mmHeight,2) + pow(mmHeight,2)]
     '''
    def motors_move(self, X1, Y1, targetX, targetY):
     
        # calculation of the line for a targetX lower than X1
        if (X1 < targetX):
            pente = (targetY - Y1) / (targetX - X1)
            coordP = ((targetY + Y1) - pente * (targetX + X1)) / 2
            nbVector = round((targetX - X1) / self.deltastep)
        else:
            if (X1 == targetX): #vertical line
                nbVector = round(abs(targetY - Y1) / self.deltastep)
            elif (X1 > targetX):
                pente = (targetY - Y1) / (targetX - X1)
                coordP = ((targetY + Y1) - pente * (targetX + X1)) / 2
                nbVector = abs(round((X1 - targetX) / self.deltastep))
        
        cptNbElement=0
        matX = []
        matY = []

        if (targetY - Y1 )>0 : sign = +1
        else: sign =-1

        #creation of matrix matX and matY which contain all coordinates X,Y for the line
        while cptNbElement <= nbVector:
            if cptNbElement==0:
                #matX will contain X coordinates
                #it's a matrice with nbVector elements
                matX.append(X1)
                matY.append(Y1)
            elif (cptNbElement == nbVector):
                matX.append(targetX)
                matY.append(targetY)
                if self.deltastep < 0 : self.deltastep = abs(self.deltastep)
            else:
                if (X1 == targetX):
                    matX.append(targetX)
                    matY.append(matY[cptNbElement - 1] + (sign* (self.deltastep)))
                elif (X1 < targetX):
                    matX.append(matX[cptNbElement - 1] + self.deltastep)
                    matY.append((pente * matX[cptNbElement]) + coordP)
                else:
                    matX.append(matX[cptNbElement - 1] - self.deltastep)
                    matY.append((pente * matX[cptNbElement]) + coordP)
            cptNbElement +=1
            
        # creation of matrix matL1 and matL2 which contain all ruber length between the pen holder and motor 1 for matL1
        #mat2 contain all lengths between motor2 and pen holder
        matL1 = []
        matL2 = []
        cptNbElement = 0

        if len(matX) == len(matY):
            while cptNbElement < len(matX):
                # calculation of the angles
                teta1inter = math.atan2((self.mmHeight - matY[cptNbElement]), matX[cptNbElement])
                teta2inter = math.atan2((self.mmHeight - matY[cptNbElement]), (self.mmWidth - matX[cptNbElement]))
                # calculation of the lengths
                L1inter = (self.mmHeight - matY[cptNbElement]) / math.sin(teta1inter)
                L2inter = (self.mmHeight - matY[cptNbElement]) / math.sin(teta2inter)
                matL1.append(L1inter)
                matL2.append(L2inter)
                cptNbElement += 1

        #
        #
        #algorithm for steps and sending instructions to the motors
        #
        cptNbElement = 1
        L1_real = matL1[0]
        L2_real = matL2[0]
        element_L1 = []
        element_L2 = []
        element_L1.append(L1_real)
        element_L2.append(L2_real)

        if len(matL1) == len(matL2):
            while cptNbElement < len(matL1):
                #MOTOR LEFT
                # test the difference between the current element and real length
                # if the difference is bigger than a revolution of a motor step, the motor has to turn
                if abs(L1_real - matL1[cptNbElement] )> self.mmPerStep :
                    time.sleep(delay_motor)
                    if L1_real > matL1[cptNbElement]:
                        L1_real -= self.looknbStep (L1_real,matL1[cptNbElement])*self.mmPerStep
                        msg="0,-"+str(self.looknbStep (L1_real,matL1[cptNbElement]))+"\0"
                        self.write_file(msg)
                        self.a.write(msg.encode())
                    else:
                        L1_real += self.looknbStep (L1_real,matL1[cptNbElement])*self.mmPerStep
                        msg="0,"+str(self.looknbStep(L1_real, matL1[cptNbElement]))+"\0"
                        self.write_file(msg)
                        element_L1.append(L1_real)
                        self.a.write(msg.encode())

                #MOTOR RIGHT
                if abs(L2_real - matL2[cptNbElement] )> self.mmPerStep :
                    time.sleep(delay_motor)
                    if L2_real > matL2[cptNbElement]:
                        L2_real -= self.looknbStep (L2_real,matL2[cptNbElement])*self.mmPerStep
                        msg="1,-"+str(self.looknbStep (L2_real,matL2[cptNbElement]))+"\0"
                        self.write_file(msg)
                        self.a.write(msg.encode())
                    else:
                        L2_real += self.looknbStep (L2_real,matL2[cptNbElement])*self.mmPerStep
                        msg="1,"+str(self.looknbStep(L2_real, matL2[cptNbElement]))+"\0"
                        self.write_file(msg)
                        self.a.write(msg.encode())
                    element_L2.append(L2_real)
                cptNbElement += 1

        self.currentX = targetX
        self.currentY = targetY
        matX.clear()
        matY.clear()
        matL1.clear()
        matL2.clear()
        element_L1.clear()
        element_L2.clear()

    '''
        end_serial() ends the connexion with arduino
    '''
    def end_serial(self):
        print("Drawbot is saying you goodbye. See you soon !")
        self.a.close()

'''
    Coord is a class for Coordinates point (X, Y)
'''
class Coord():
    def __init__(self, x, y, lg):
        self.x = x
        self.y = y
        self.length = lg
