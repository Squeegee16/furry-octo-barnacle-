import math

def cal_space(area,pspacing, qty):
    ''' calculate planting area and percent of planting container used'''
    q = int(qty)
    A = float(area)
    try:
        rad = float(pspacing)/2
        print(type(rad),rad)
        Punit = (rad*rad)*math.pi
        Aused = float("{:.2f}".format(Punit*q))
        pcentused = float("{:.2f}".format((Aused/A)*100))
    except ZeroDivisionError:
        print('division error check input area')
        Aused = -0.0
        pcentused = -0.0
    print(Aused, pcentused)

cal_space(6960.0,24,2)

