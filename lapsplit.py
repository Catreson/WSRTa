import os
import pandas as pd
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup

def find_laps(data, start_line, minimal_laptime = 30, finish_line_tolerance = 0.1):
    
    start_time = data['timestamp'].values[0]
    last_lap_time = start_time
    lap_indices = []
    line_lenght = np.sqrt((start_line[0][0] - start_line[1][0])**2 + (start_line[0][1] - start_line[1][1])**2)

    for i in range(1, len(data)):
        if (np.sqrt((data['longitude'].values[i] - start_line[0][0])**2 + 
                   (data['latitude'].values[i] - start_line[0][1])**2)  +
            np.sqrt((data['longitude'].values[i] - start_line[1][0])**2 + 
                   (data['latitude'].values[i] - start_line[1][1])**2) < line_lenght*(1+finish_line_tolerance)):
            if data['timestamp'].values[i] - last_lap_time > minimal_laptime:
                lap_indices.append((last_lap_time, data['timestamp'].values[i]))
                last_lap_time = data['timestamp'].values[i]
                
    if lap_indices:
        lap_indices[0] = (start_time, lap_indices[0][1])
    
    return np.array(lap_indices)

def save_laptimes(laps, path=""):
        with open(f'{path}laptimes.csv', 'w') as lapfile:
            lapfile.write('lap_number,lap_time\n')
            for i, lap in enumerate(laps, 1):
                lapfile.write(f'{i},{lap[1] - lap[0]}\n')

def split_laps(data, laps):

    laps_data = []
    
    for i in range(len(laps)):
        if i == 0:
            start_index = 0
        else:
            start_index = data[data['timestamp'] == laps[i-1][1]].index[0] + 1
            
        end_index = data[data['timestamp'] == laps[i][1]].index[0]
        
        laps_data.append(data.iloc[start_index:end_index+1])
        
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

    laps = find_laps(data, start_line)

    save_laptimes(laps)

    laps_data = split_laps(data, laps)

    for i, lap in enumerate(laps_data):
        lap.to_csv(f'lap_{i+1}.csv', index=False)