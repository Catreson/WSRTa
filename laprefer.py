import os
import re
import pandas as pd
import math
from geopy import distance
from pathlib import Path
from lap import Lap
from bs4 import BeautifulSoup

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
    print('Refering...')
    index_list = {lap.ID:0 for lap in laps}
    vals = {lap.ID:[] for lap in laps}
    reference_lap = None
    for lap in laps:
        if lap.ID == reference_lap_ID:
            reference_lap = lap
    if reference_lap == None:
        print('Wrong reference lap')
        return
    for i, row in reference_lap.df.iterrows():
        rad_argument = ((2 * math.pi - math.radians(row['course'])) + math.pi/2) % (2 * math.pi)
        deformation = distance.distance((row['latitude'], row['longitude']), (row['latitude'] + 0.0002, row['longitude'])).m\
                                        / distance.distance((row['latitude'], row['longitude']), (row['latitude'], row['longitude'] + 0.0002)).m
        argument = -1.0 / math.tan(rad_argument)
        argument = argument / deformation
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

def getLaps(path, **kwargs):
    acc_met = kwargs.get('acc_met', 0)

    if not os.path.exists(path):
        return
    dir_path = Path(path).parent
    laps = [Lap(ID = x.stem, df = pd.read_csv(x), path = x) for x in Path(dir_path).iterdir() if x.is_file() and Path(x).suffix == '.lap']
    with open(path, 'r') as file:
        times_data = file.read()
    bs_times_data = BeautifulSoup(times_data, 'xml')
    bs_laptimes = bs_times_data.find_all('lap')
    time_dic = {x.get('number'): '{:.3f}'.format(float(x.get_text())) for x in bs_laptimes}
    
    rex = re.compile('_\d+')
    laps.sort(key = lambda x: int(rex.findall(x.ID)[0][1:]))
    for i, lap in enumerate(laps):
        lap.calculateTrackDistance()
        if acc_met == 0:
            lap.calculateAcceleration()
        else:
            lap.calculateAcceleration2()

        if lap.ID in time_dic:
            lap.setLaptime(time_dic[lap.ID])
        else:
            lap.findLaptime()
        lap.color = Lap.choosable_colors[i % len(Lap.choosable_colors)]
    laps_dic = {x.ID: x for x in laps}
    return laps_dic

def perpendicularLine(lat, lon, course, lenght):
    coords = []
    lon_lenght = 0.0001 * (lenght / distance.distance((lat, lon), (lat, lon + 0.0001)).m)
    deformation = distance.distance((lat, lon), (lat + 0.0002, lon)).m\
                    / distance.distance((lat, lon), (lat, lon + 0.0002)).m
    rad_argument = ((2 * math.pi - math.radians(course)) + math.pi/2) % (2 * math.pi)
    argument = -1.0 / math.tan(rad_argument)
    argument = argument / deformation
    b =  lat - lon * argument
    additional_distance = (lon_lenght / 2) / math.sqrt(1 + argument**2)
    tmp = lon + additional_distance
    coords.append((argument * tmp + b, tmp))
    tmp = lon - additional_distance
    coords.append((argument * tmp + b, tmp))
    return coords

if __name__ == '__main__':
    print("Don't")