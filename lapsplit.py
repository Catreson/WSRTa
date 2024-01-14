import os
from math import sqrt
import pandas as pd
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from geopy import distance
import utm
from numba import njit

@njit
def calculateDistance(A, B, C, x, y):
    return abs(A*x + B* y + C) / sqrt(A*A + B*B)

@njit
def compareDistance(A, B, C, x1, y1, x2, y2):
    if calculateDistance(A, B, C, x1, y1) > calculateDistance(A, B, C, x2, y2):
        return True
    return False

def winStartElipse(lat, lon, line, coef):
    d = distance.distance((line[0][1], line[0][0]), (lat, lon)).m
    d += distance.distance((line[1][1], line[1][0]), (lat, lon)).m
    return d <= coef * distance.distance((line[0][1], line[0][0]), (line[1][1], line[1][0])).m

@njit
def winStartElipseUtm(lat, lon, coef, line_length, line = np.array([[]])):
    return sqrt((line[0][1] - lat)*(line[0][1] - lat) + (line[0][0] - lon)*(line[0][0] - lon)) + sqrt((line[1][1] - lat)*(line[1][1] - lat) + (line[1][0] - lon)*(line[1][0] - lon))\
        <= coef * line_length

def findLaps(data, start_line, minimal_laptime = 30, finish_line_tolerance = 0.5):
    start_time = data['timestamp'].values[0]
    last_lap_time = start_time
    lap_indices = []
    y1, x1, du, mp = utm.from_latlon(np.array([start_line[0][1], start_line[1][1]]), np.array([start_line[0][0], start_line[1][0]]))
    lat1_utm = y1[0]
    lat2_utm = y1[1]
    lon1_utm = x1[0]
    lon2_utm = x1[1]

    start_line_utm = np.array([[x1[0], y1[0]], [x1[1], y1[1]]])
    a_utm = (lat2_utm - lat1_utm) / (lon2_utm - lon1_utm)
    b_utm = lat2_utm - a_utm * lon2_utm
    distance_utm = sqrt((lat2_utm - lat1_utm)**2 + (lon2_utm - lon1_utm)**2)
    tripwire_utm = {'A':a_utm, 'B': -1, 'C':b_utm}
    arr_lat, arr_lon, du, mp = utm.from_latlon(np.asarray(data['latitude']), np.asarray(data['longitude']))
    arr =np.array([arr_lat[1:],
          arr_lon[1:],
          [t for t in data['timestamp'][1:]]])
    p_lat = arr_lat[0]
    p_lon = arr_lon[0]
    p_t = data['timestamp'][0]
    for row in np.nditer(arr, flags=['external_loop'], order='F'):
        if winStartElipseUtm(p_lat, p_lon, finish_line_tolerance, distance_utm, start_line_utm)\
              and not compareDistance(tripwire_utm['A'], tripwire_utm['B'], tripwire_utm['C'], p_lon, p_lat, row[1], row[0]):
            if row[2] - last_lap_time > minimal_laptime:
                lap_indices.append((last_lap_time, p_t))
                last_lap_time = p_t
        p_lat = row[0]
        p_lon = row[1]
        p_t = row[2]
                
    if lap_indices:
        lap_indices[0] = (start_time, lap_indices[0][1])
    
    return np.array(lap_indices)

def saveLaptimes(laps, path=""):
        with open(f'{path}laptimes.csv', 'w') as lapfile:
            lapfile.write('lap_number,lap_time\n')
            for i, lap in enumerate(laps, 1):
                lapfile.write(f'{i},{lap[1] - lap[0]}\n')

def splitLaps(data, laps):

    laps_data = []
    
    for i in range(len(laps)):
        if i == 0:
            start_index = 0
        else:
            start_index = data[data['timestamp'] == laps[i-1][1]].index[0] + 1
            
        end_index = data[data['timestamp'] == laps[i][1]].index[0]
        
        laps_data.append(data.iloc[start_index:end_index+2])
        
    return laps_data

def createSessionFile(path, laps, **kwargs):
    p = Path(path)
    laps_path = Path.cwd() / p.stem
    if not os.path.isdir(laps_path):
        os.mkdir(laps_path)
    with open(laps_path / f'{p.stem}.wsrtses', 'wb') as file:
        rut = ET.Element('session')
        details = ET.SubElement(rut, 'details')
        laplist = []
        laptimes = ET.SubElement(rut, 'laptimes')
        rider_name = ET.SubElement(details, 'rider_name')
        rider_name.text = kwargs.get('session_rider', 'Twoja stara')
        track_name = ET.SubElement(details, 'track_name')
        track_name.text = kwargs.get('session_track', 'Autodromo Nazionale di Radom')
        ride_date = ET.SubElement(details, 'date')
        ride_date.text = kwargs.get('session_date', '1970-01-01')
        ride_id = ET.SubElement(details, 'identifier')
        ride_id.text = kwargs.get('session_id', 'session')
        no_laps = ET.SubElement(laptimes, 'no_laps')
        no_laps.text = str(len(laps))
        tag = kwargs.get('session_id', 'get')
        for i, lap in enumerate(laps, 1):
            tmp = ET.SubElement(laptimes, f'lap')
            tmp.set('number', f'{tag}_{i}')
            tmp.text = str(lap[1] - lap[0])
            laplist.append(tmp)
        tmp = minidom.parseString(ET.tostring(rut)).toprettyxml(indent="   ")
        file.write(tmp.encode('utf-8'))
    return laps_path, tag

def saveLaps(path, laps_data, tag):
    if not tag:
        tag = 'l'
    for i, lap in enumerate(laps_data):
        lap.to_csv(f'{path}/{tag}_{i+1}.lap', index=False)

if __name__ == "__main__":

    data = pd.read_csv('radominter.csv')


    start_line = [(21.149420, 51.417095), (21.149489, 51.417186)]

    laps = findLaps(data, start_line)

    saveLaptimes(laps)

    laps_data = splitLaps(data, laps)

    for i, lap in enumerate(laps_data):
        lap.to_csv(f'lap_{i+1}.csv', index=False)