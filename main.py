# -*- coding: utf-8 -*-
#main.py
#author: Drawnie team CRI
#date : november 2019
#version : V1.0


#import Drawbot and Coord classes for the Drawing system
from drawnie import Drawbot
from drawnie import Coord

'''
    ask_function() : is a function to ask the mode of the Drawbot
    It returns : 1, 2 or 3
    1 is for drawing a line
    2 is for drawing a square
    3 is for leaving the program
'''
def ask_function():
    try:
        choice = int(input("Enter 1 for a line, 2 for a square, 3 to leave Drawbot "))
    except ValueError:
        print ("Not a digit.")
    if (choice < 1 or choice > 3):
        print ("Not valid")
        return ask_function()
    return choice

'''
    ask_coordinates_point() : is a function to verify that point are in the Drawing zone
    It returns a Coord point 
'''
def ask_coordinates_point(msg):
    try:

        # min and max point for the drawing area
        minX = drawnie.marginX
        maxX = drawnie.mmWidth-drawnie.marginX
        minY = drawnie.marginY
        maxY = drawnie.mmHeight-drawnie.marginY
        print("To draw a line,")
        x, y = input("Enter the %s point X Y "%(msg)).split()

    except ValueError:
        print ("Misses one coordinate")
        return ask_coordinates_point()

    # test is x is a digit
    if x.isdigit() == False:
        print ("X is not a digit.")
        print("It should belongs to the interval %s and %s"%(minX, maxX))
        return ask_coordinates_point()

    # test is y is a digit
    if y.isdigit() == False:
        print ("Y is not a digit.")
        print("It should belongs to the interval %s and %s"% (minY, maxY))
        return ask_coordinates_point()

    # convert the strings received in int
    x = int(x)
    y = int(y)

    # test x or y belongs to the intervals of the drawing area
    if (x < minX or x > maxX) or (y < minY or y > maxY):
        print ("Coordinates are not valid.")
        print("X should belongs to the interval %s and %s"%(minX, maxX))
        print("Y should belongs to the interval %s and %s" % (minY, maxY))
        return ask_coordinates_point()

    # creates the point to start
    sendPoint = Coord(x,y,0)
    return sendPoint


'''
    ask_square() : is a function to verify that a square is correctly drawn
    It returns a Coord point with a length
'''
def ask_square():
    try:
        # min and max point for the drawing area
        minX = drawnie.marginX
        maxX = drawnie.mmWidth-drawnie.marginX
        minY = drawnie.marginY
        maxY = drawnie.mmHeight-drawnie.marginY
        print("To draw a square,")
        x, y, lg = input("Enter a beginning point and a length :  X Y length ").split()

    except ValueError:
        print ("Misses one coordinate")
        return ask_square()

    #test is x is a digit
    if x.isdigit() == False:
        print ("X is not a digit.")
        print("It should belongs to the interval %s and %s"%(minX, maxX))
        return ask_square()

    # test is y is a digit
    if y.isdigit() == False:
        print ("Y is not a digit.")
        print("It should belongs to the interval %s and %s"% (minY, maxY))
        return ask_square()

    # test is length is a digit
    if lg.isdigit() == False:
        print ("Length is not a digit.")
        return ask_square()

    # convert the strings received in int
    x = int(x)
    y = int(y)
    lg = int(lg)

    # test x or y belongs to the intervals of the drawing area
    if (x < minX or x > maxX) or (y < minY or y > maxY):
        print ("Coordinates are not valid.")
        print("X should belongs to the interval %s and %s"%(minX, maxX))
        print("Y should belongs to the interval %s and %s" % (minY, maxY))
        return ask_square()

    if ((x+ lg)>maxX) or ((y+lg)>maxY):
        print("Length is too big.")
        return ask_square()

    # creates the point to start
    sendPoint = Coord(x,y, lg)
    return sendPoint

#initialization of the Drawbot class
drawnie = Drawbot()

#loop for the program
while 1 :
    #function to receive User informations for instructions
    choice = ask_function()
    #draw a line
    if choice == 1:
        point1 = ask_coordinates_point("beginning")
        point2 = ask_coordinates_point("ending")
        drawnie.drawStraightline(point1.x, point1.y, point2.x, point2.y)
        drawnie.reinit_drawing()

    # draw a square
    if choice == 2:
        point1 = ask_square()
        drawnie.drawSquare (point1.x,point1.y,point1.length)
        drawnie.reinit_drawing()

    # leave the program
    if choice == 3:
        drawnie.end_serial()
        exit()

