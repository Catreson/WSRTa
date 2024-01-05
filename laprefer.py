import pandas as pd
import numpy as np
import math
from geopy import distance
from lapsplit import Lap

def referLapsToLap1(laps = ['l0',pd.DataFrame()], reference_lap_index = 0, reference_lap_ID='l0'):
    for name in laps:
        print(name[0])
    index_list = {name[0]:0 for name in laps}
    vals = {name[0]:[] for name in laps}
    for line in list(zip(laps[reference_lap_index][1]['latitude'], laps[reference_lap_index][1]['longitude'], laps[reference_lap_index][1]['course'])):
        rad_argument = ((2 * math.pi - math.radians(float(line[2]))) + math.pi/2) % (2 * math.pi)
        argument = -1.0 / math.tan(rad_argument)
        b =  float(line[0]) - float(line[1]) * argument
        tripwire = {'A':argument, 'B': -1, 'C':b}
        #print(f'Lat: {line[0]}, Calculated_lat: {tripwire["A"] * float(line[1]) + tripwire["C"]}')
        def calculateDistance(A, B, C, x, y):
            #print(f'Distance: {abs(A*x + B* y + C) / math.sqrt(A**2 + B**2)}')
            return abs(A*x + B* y + C) / math.sqrt(A**2 + B**2)
        def compareDistance(A, B, C, x1, y1, x2, y2):
            if calculateDistance(A, B, C, x1, y1) > calculateDistance(A, B, C, x2, y2):
                return True
            return False
        for lap in laps:
            if lap[0] != reference_lap_ID:
                if index_list[lap[0]] < len(lap[1]['longitude']) - 2:
                    x1 = lap[1]['longitude'][index_list[lap[0]]]
                    x2 = lap[1]['longitude'][index_list[lap[0]] + 1]
                    y1 = lap[1]['latitude'][index_list[lap[0]]]
                    y2 = lap[1]['latitude'][index_list[lap[0]] + 1]
                    cnt = 0
                    while compareDistance(tripwire['A'], tripwire['B'], tripwire['C'], x1, y1, x2, y2) and index_list[lap[0]] < len(lap[1]['longitude']) - 2:
                        index_list[lap[0]] += 1
                        x1 = lap[1]['longitude'][index_list[lap[0]]]
                        x2 = lap[1]['longitude'][index_list[lap[0]] + 1]
                        y1 = lap[1]['latitude'][index_list[lap[0]]]
                        y2 = lap[1]['latitude'][index_list[lap[0]] + 1]
                vals[lap[0]].append(index_list[lap[0]])
    for lap in laps:
        if lap[0] != reference_lap_ID:
            laps[reference_lap_index][1][lap[0]] = vals[lap[0]]
    print('Refering complete')

def referLapsToLap(laps = [Lap()], reference_lap_ID='l0'):
    index_list = {lap.ID:0 for lap in laps}
    vals = {lap.ID:[] for lap in laps}
    reference_lap = None
    for lap in laps:
        if lap.ID == reference_lap_ID:
            reference_lap = lap
    if reference_lap == None:
        return
    for i, row in reference_lap.df.iterrows():
        rad_argument = ((2 * math.pi - math.radians(row['course'])) + math.pi/2) % (2 * math.pi)
        deformation = distance.distance((row['latitude'], row['longitude']), (row['latitude'] + 0.0002, row['longitude'])).m\
                                        / distance.distance((row['latitude'], row['longitude']), (row['latitude'], row['longitude'] + 0.0002)).m
        argument = -1.0 / math.tan(rad_argument)
        #argument = argument / deformation
        b =  row['latitude'] - row['longitude'] * argument
        tripwire = {'A':argument, 'B': -1, 'C':b}
        def calculateDistance(A, B, C, x, y):
            return abs(A*x + B* y + C) / math.sqrt(A**2 + B**2)
        def compareDistance(A, B, C, x1, y1, x2, y2):
            if calculateDistance(A, B, C, x1, y1) > calculateDistance(A, B, C, x2, y2):
                return True
            return False
        for lap in laps:
            if lap.ID != reference_lap_ID:
                if index_list[lap.ID] < len(lap.df['longitude']) - 2:
                    x1 = lap.df['longitude'][index_list[lap.ID]]
                    x2 = lap.df['longitude'][index_list[lap.ID] + 1]
                    y1 = lap.df['latitude'][index_list[lap.ID]]
                    y2 = lap.df['latitude'][index_list[lap.ID] + 1]
                    while compareDistance(tripwire['A'], tripwire['B'], tripwire['C'], x1, y1, x2, y2) and index_list[lap.ID] < len(lap.df['longitude']) - 2:
                        index_list[lap.ID] += 1
                        x1 = lap.df['longitude'][index_list[lap.ID]]
                        x2 = lap.df['longitude'][index_list[lap.ID] + 1]
                        y1 = lap.df['latitude'][index_list[lap.ID]]
                        y2 = lap.df['latitude'][index_list[lap.ID] + 1]
                vals[lap.ID].append(index_list[lap.ID])
    for lap in laps:
        if lap.ID != reference_lap_ID:
            reference_lap.df[lap.ID] = vals[lap.ID][:len(reference_lap.df['latitude'])]
    print('Refering complete')

def referLapsToLap2(laps = [Lap()], reference_lap_ID='l0'):
    index_list = {lap.ID:0 for lap in laps}
    vals = {lap.ID:[] for lap in laps}
    reference_lap = None
    prev_lat = 0
    prev_lon = 0
    for lap in laps:
        if lap.ID == reference_lap_ID:
            reference_lap = lap
    if reference_lap == None:
        return
    for i, row in reference_lap.df.iterrows():
        if i == 0:
            prev_lat = 0
            prev_lon = 0
            rad_argument = ((2 * math.pi - math.radians(row['course'])) + math.pi/2) % (2 * math.pi)
            argument = -1.0 / math.tan(rad_argument)
        else:
            argument = (row['latitude'] - prev_lat) / (row['longitude'] - prev_lon)
            argument = -1 / argument
        b =  row['latitude'] - row['longitude'] * argument
        tripwire = {'A':argument, 'B': -1, 'C':b}
        def calculateDistance(A, B, C, x, y):
            return abs(A*x + B* y + C) / math.sqrt(A**2 + B**2)
        def compareDistance(A, B, C, x1, y1, x2, y2):
            if calculateDistance(A, B, C, x1, y1) > calculateDistance(A, B, C, x2, y2):
                return True
            return False
        for lap in laps:
            if lap.ID != reference_lap_ID:
                if index_list[lap.ID] < len(lap.df['longitude']) - 2:
                    x1 = lap.df['longitude'][index_list[lap.ID]]
                    x2 = lap.df['longitude'][index_list[lap.ID] + 1]
                    y1 = lap.df['latitude'][index_list[lap.ID]]
                    y2 = lap.df['latitude'][index_list[lap.ID] + 1]
                    while compareDistance(tripwire['A'], tripwire['B'], tripwire['C'], x1, y1, x2, y2) and index_list[lap.ID] < len(lap.df['longitude']) - 2:
                        index_list[lap.ID] += 1
                        x1 = lap.df['longitude'][index_list[lap.ID]]
                        x2 = lap.df['longitude'][index_list[lap.ID] + 1]
                        y1 = lap.df['latitude'][index_list[lap.ID]]
                        y2 = lap.df['latitude'][index_list[lap.ID] + 1]
                vals[lap.ID].append(index_list[lap.ID])
    for lap in laps:
        if lap.ID != reference_lap_ID:
            reference_lap.df[lap.ID] = vals[lap.ID][:len(reference_lap.df['latitude'])]
    print('Refering complete')
        
def calculateTrackDistance(lap = pd.DataFrame()):
    distances = []
    prev_lat = 0
    prev_lon = 0
    suma = 0 
    for i, line in enumerate(list(zip(lap['latitude'], lap['longitude']))):
        if i == 0:
            distances.append(0)
            prev_lat = line[0]
            prev_lon = line[1]
            continue
        curr_step = distance.distance((prev_lat, prev_lon), (line[0], line[1])).m
        suma += curr_step
        distances.append(suma)
        prev_lat = line[0]
        prev_lon = line[1]
    lap['distance'] = distances            
        
def calculateAcceleration(lap = pd.DataFrame()):
    kmh_to_ms = 1.0/3.6
    g_force_to_m_s2 = 9.81
    m_s2_to_g_force = 1 / g_force_to_m_s2

    acc_t_list = []
    acc_n_list = []
    corner_radius_list = []

    prev_v = 0
    prev_s = 0
    prev_fi = 0
    prev_time = 0
    for i, row in lap.iterrows():
        if i == 0:
            acc_t_list.append(0)
            acc_n_list.append(0)
            corner_radius_list.append(0)
            prev_v = row['gps_speed']
            prev_s = row['distance']
            prev_fi = math.radians(row['course'])
            prev_time = row['timestamp']
            continue
        acc_t = kmh_to_ms * (row['gps_speed'] - prev_v) / (row['timestamp'] - prev_time)
        if math.radians(row['course']) - prev_fi != 0:
            if abs(row['course'] - math.degrees(prev_fi)) > 90:
                if row['course'] > math.degrees(prev_fi):
                    corner_radius = (row['distance'] - prev_s) / ((math.radians(row['course']) - prev_fi) - 2*math.pi)
                else:
                    corner_radius = (row['distance'] - prev_s) / ((math.radians(row['course']) - prev_fi) + 2*math.pi)
            else:
                corner_radius = (row['distance'] - prev_s) / (math.radians(row['course']) - prev_fi)
        else:
            corner_radius = np.inf
                
        acc_n = (kmh_to_ms * (row['gps_speed'] + prev_v) / 2)**2 / corner_radius if corner_radius != 0 else np.inf
        prev_fi = math.radians(row['course'])
        prev_v = row['gps_speed']
        prev_s = row['distance']
        prev_time = row['timestamp']
        acc_t_list.append(acc_t)
        acc_n_list.append(acc_n)
        corner_radius_list.append(corner_radius)
    lap['acc_n'] = acc_n_list
    lap['acc_t'] = acc_t_list
    lap['acc_n_g'] = [m_s2_to_g_force * x for x in acc_n_list]
    lap['acc_t_g'] = [m_s2_to_g_force * x for x in acc_t_list]
    lap['radius'] = corner_radius_list

def calculateAcceleration2(lap = pd.DataFrame()):
    kmh_to_ms = 1.0/3.6
    g_force_to_m_s2 = 9.81
    m_s2_to_g_force = 1 / g_force_to_m_s2
    acc_t_list = []
    acc_n_list = []
    corner_radius_list = []

    prev_v = 0
    prev_fi = 0
    prev_time = 0
    for i, row in lap.iterrows():
        if i == 0:
            acc_t_list.append(0)
            acc_n_list.append(0)
            corner_radius_list.append(0)
            prev_v = row['gps_speed']
            prev_fi = math.radians(row['course'])
            prev_time = row['timestamp']
            continue
        acc_t = kmh_to_ms * (row['gps_speed'] - prev_v) / (row['timestamp'] - prev_time)

        if abs(row['course'] - math.degrees(prev_fi)) > 90:
            if row['course'] > math.degrees(prev_fi):
                acc_n = (kmh_to_ms * (row['gps_speed'] + prev_v) / 2) * (((math.radians(row['course']) - prev_fi) - 2*math.pi) / (row['timestamp'] - prev_time))
            else:
                acc_n = (kmh_to_ms * (row['gps_speed'] + prev_v) / 2) * (((math.radians(row['course']) - prev_fi) + 2*math.pi) / (row['timestamp'] - prev_time))
        else:
            acc_n = (kmh_to_ms * (row['gps_speed'] + prev_v) / 2) * ((math.radians(row['course']) - prev_fi) / (row['timestamp'] - prev_time))


        corner_radius = ((kmh_to_ms * (row['gps_speed'] + prev_v) / 2)**2) / acc_n if acc_n != 0 else np.inf

        prev_fi = math.radians(row['course'])
        prev_v = row['gps_speed']
        prev_time = row['timestamp']
        acc_t_list.append(acc_t)
        acc_n_list.append(acc_n)
        corner_radius_list.append(corner_radius)
    lap['acc_n2'] = acc_n_list
    lap['acc_t2'] = acc_t_list
    lap['acc_n_g2'] = [m_s2_to_g_force * x for x in acc_n_list]
    lap['acc_t_g2'] = [m_s2_to_g_force * x for x in acc_t_list]
    lap['radius2'] = corner_radius_list