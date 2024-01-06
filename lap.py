import math
import numpy as np
import pandas as pd
from geopy import distance
class Lap:
    def __init__(self, **kwargs):
        self.df = kwargs.get('df', None)
        self.ID = kwargs.get('ID', None)
        self.color = kwargs.get('color', None)
        self.laptime = kwargs.get('laptime', None)
        self.path = kwargs.get('path', None)

    choosable_colors = ['red',
                    'green',
                    'blue',
                    'yellow',
                    'orange',
                    'purple',
                    'cyan',
                    'magenta']
    
    def findLaptime(self):
        if isinstance(self.df, pd.DataFrame):
            start_time = self.df['timestamp'][0]
            end_time = self.df['timestamp'].iloc[-1]
            self.laptime = end_time - start_time
    def setDf(self, df):
        self.df = df
    def setLaptime(self, laptime):
        self.laptime = laptime

    def saveLap(self):
        self.df.to_csv(self.path)

    def calculateTrackDistance(self):
        distances = []
        lap = self.df
        prev_lat = 0
        prev_lon = 0
        suma = 0 
        if 'distance' in lap:
            return
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

    def calculateAcceleration2(self, **kwargs):
        kmh_to_ms = 1.0/3.6
        g_force_to_m_s2 = 9.81
        m_s2_to_g_force = 1 / g_force_to_m_s2
        acc_t_list = []
        acc_n_list = []
        corner_radius_list = []
        lap = self.df

        prev_v = 0
        prev_fi = 0
        prev_time = 0
        if 'acc_n' in lap:
            return
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
        lap['acc_n'] = acc_n_list
        lap['acc_t'] = acc_t_list
        lap['acc_n_g'] = [m_s2_to_g_force * x for x in acc_n_list]
        lap['acc_t_g'] = [m_s2_to_g_force * x for x in acc_t_list]
        lap['radius'] = corner_radius_list

    def calculateAcceleration(self):
        kmh_to_ms = 1.0/3.6
        g_force_to_m_s2 = 9.81
        m_s2_to_g_force = 1 / g_force_to_m_s2
        lap = self.df

        acc_t_list = []
        acc_n_list = []
        corner_radius_list = []

        prev_v = 0
        prev_s = 0
        prev_fi = 0
        prev_time = 0
        if 'acc_n' in lap.columns:
            return
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
                    
        
