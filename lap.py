import math
import numpy as np
import statistics
import pandas as pd
from geopy import distance
from pykalman import KalmanFilter
from numba import njit
import statsmodels.api as sm
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
        lap = self.df
        if 'distance' in lap:
            start = lap['distance'][0]
            distances = list(map(lambda x: x - start, lap['distance']))
            lap['distance'] = distances
            return
        distances = []
        prev_lat = 0
        prev_lon = 0
        suma = 0 
        distances.append(0)
        prev_lat = lap['latitude'][0]
        prev_lon = lap['longitude'][0]
        for line in zip(lap['latitude'], lap['longitude']):
            curr_step = distance.distance((prev_lat, prev_lon), (line[0], line[1])).m
            suma += curr_step
            distances.append(suma)
            prev_lat = line[0]
            prev_lon = line[1]
        lap['distance'] = distances

    def calculateAcceleration2(self, **kwargs):
        lap = self.df
        if 'acc_n' in lap:
            return
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
        lap['acc_n'] = acc_n_list
        lap['acc_t'] = acc_t_list
        lap['acc_n_g'] = [m_s2_to_g_force * x for x in acc_n_list]
        lap['acc_t_g'] = [m_s2_to_g_force * x for x in acc_t_list]
        lap['radius'] = corner_radius_list

    def calculateAcceleration(self):
        lap = self.df
        if 'acc_n' in lap.columns:
            return
        kmh_to_ms = 1.0/3.6
        g_force_to_m_s2 = 9.80665
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
                    
    def simpleSmoother(self, window = 30, weight = 0.8, max_diff = 0.2, tag = 'acc_n_g'):
        series = []
        for i in range(window):
            series.append(self.df[tag].iloc[i])
        for i in range(window, len(self.df[tag])-window):
            mean1 = statistics.mean(self.df[tag][i-window:i])
            mean2 = statistics.mean(self.df[tag][i+1:i+window+1]) 
            mean = statistics.mean([mean1, mean2])
            if self.df[tag].iloc[i] - mean > self.df[tag].iloc[i] * max_diff:
                series.append(mean)
            else:
                series.append(mean * weight + (1-weight) * self.df[tag].iloc[i])
        for i in range(len(series), len(series) + window):
            series.append(self.df[tag].iloc[i])
        self.df[f'{tag}_SS'] = series
    def simpleSmoother1(self, tag = 'acc_n_g'):
        series = self.df[tag]
        kf = KalmanFilter(transition_matrices=[1],
                      observation_matrices=[1],
                      initial_state_mean=series.iloc[0],
                      initial_state_covariance=1,
                      observation_covariance=1,
                      transition_covariance=0.01)
        means, coef = kf.filter(series)
        flatted = means.flatten()
        self.df[f'{tag}_SK'] = flatted


