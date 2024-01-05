import numpy as np
import math
import time
from multiprocessing import shared_memory, resource_tracker

pi = math.pi
last_time = 0

track_width = 10                                   
erath_radius = 6371000                

fiSM=52.3017417 #latitude finish line
lambdaSM=20.935266666666667 #longitude finish line

window_lenght = 1


GPS_RAW = [1.1, 2.2, 3.3]

k = 0 
flag = 0
lap = 0 

qx = []
qy = []


lambdaSM = math.radians(lambdaSM) 
fiSM = math.radians(fiSM)

xs = 0
ys = 0 

XO=GPS_READ[0]
YO=GPS_READ[1]
first_time = GPS_READ[2]
last_time=first_time
best_time = 10000000000000
for i in range(No):
    qx.insert(0, r*math.cos(fiSM)*(math.radians(GPS_READ[0]) - lambdaSM))
    qy.insert(0,r*(math.radians(GPS_READ[1]) - fiSM))

while True:
    
    
    GPS_RAW[:] = GPS_READ[:]
    #% actual GPS point
    XN = r*math.cos(fiSM)*(math.radians(GPS_RAW[0]) - lambdaSM) 
    YN = r*(math.radians(GPS_RAW[1]) - fiSM) 
    #print(GPS_RAW[0])
    #print(GPS_RAW[1])

    #% centre point of window
    Xc = (XN + XO)/2 
    Yc = (YN + YO)/2 
    
    try:
        alfa = math.atan((YN - YO)/(XN - XO))    #% slope of the line between the actual and prev. GPS point
    except ZeroDivisionError:
        qx.insert(0, XN)
        qy.insert(0, YN)
        XO=qx.pop()
        YO=qy.pop()
        continue
    h = math.sqrt((XO - XN)**2 + (YO - YN)**2)  #% window height
    
    #% angle for rotation matrix
    if XN >= XO:
        theta = -pi/2 + alfa 
    else:
        theta = pi/2 + alfa 
    
    R = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])  #% rotation matrix
    
    p1 = np.add(np.matmul(R, [[- w/2],[h/2]]), [[Xc],[Yc]])     #% top-left rectancle corner
    p2 = np.add(np.matmul(R, [[w/2],[h/2]]), [[Xc],[Yc]])       #% top-right rectangle corner
    p3 = np.add(np.matmul(R, [[w/2],[-h/2]]), [[Xc],[Yc]])      #% bottom-right rectangle corner
    p4 = np.add(np.matmul(R, [[- w/2],[-h/2]]), [[Xc],[Yc]])    #% bottom-left rectangle corner
    
    p21 = np.array([p2[0] - p1[0],p2[1] - p1[1]])   #% vector p1->p2
    p41 = np.array([p4[0] - p1[0],p4[1] - p1[1]])   #% vector p1->p4

    
    p21mSq = (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2  #% square length of vector p1->p2
    p41mSq = (p4[0] - p1[0])**2 + (p4[1] - p1[1])**2  #% square length of vector p1->p4
    
    ps1 = np.array([xs - p1[0],ys - p1[1]])     #% vector p1->(trigger point)
    #ps1 = ps1.transpose()
    
     
   
    if flag == 1:
        if ps1[0]*p21[0] + ps1[1]*p21[1] <= p21mSq and ps1[0]*p21[0] + ps1[1]*p21[1] >= 0:
            if ps1[0]*p41[0] + ps1[1]*p41[1] <= p41mSq and ps1[0]*p41[0] + ps1[1]*p41[1] >= 0:
          
                lap = lap+1 
                k = 0 
                cur_time = GPS_RAW[2]
                lap_time = cur_time - last_time
                last_time = cur_time
                full_time = cur_time - first_time
                if lap > 0:
                    delta = best_time - lap_time
                if lap_time < best_time:
                    
                    best_time = lap_time
                #line = "okr" + str(lap)
                with open('beacon.txt', 'a') as f:
                    f.write(str(time.time()) + '\n')
                print("okrazenie" + str(lap_time))
                disp[13] = lap_time
                disp[14] = delta
                #% --- PSEUDOKOD --- #%
                #% 1. zapisz czas okrazenia (np. jako zmienna "Segment
                #% Times") i wyswietl
                #% 2. zapisz calkowity czas od poczatku logowanego pliku
                #% jako np. "Beacon Marker", ktory to pozniej bedzie
                #% wykorzystywany do podzialu plikow na okrazenia w
                #% aplikacji do analizy danych
                #% 3. rozpocznij stoper dla nowego okrazenia
                
                
       
    
    
    #% zabezpieczenie, jesli trigger znajdzie się w kolejnych, nastepujacych
    #% po sobie oknach to nie potraktuje tego jako nowe okrazenie
    if k <= 10:
        k = k+1 
        flag = 0 
    else:
        flag = 1 
    qx.insert(0, XN)
    qy.insert(0, YN)
    XO=qx.pop()
    YO=qy.pop()
        
    

