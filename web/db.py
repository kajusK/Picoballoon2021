import sqlite3
import os
from collections import defaultdict

class Database:

    def __init__(self, path):
        self.__connection = sqlite3.connect(f'{path}/database.sqlite')
        self.__connection.execute('pragma journal_mode=wal')
        self.__cursor = self.__connection.cursor()
        self.create_database_structure()

    def create_database_structure(self):
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                timestamp INTEGER,
                pressure_pa INTEGER,
                temp_c REAL,
                core_temp_c REAL,
                alt_m INTEGER,
                lat REAL,
                lon REAL,
                bat_mv INTEGER,
                loop_time_s INTEGER,
                lat_gw REAL,
                lon_gw REAL,
                alt_gw INTEGER,
                freq REAL,
                rssi INTEGER,
                json TEXT)''')

    def identify_strongest_gw(self, metadata):
        '''
        Determine strongest RSSI from an array of gateways,
        return strongest gateway latitude, longitude, altitude and rssi
        if essential values are absent, return None
        '''
        rssi = None
        lat_gw = None
        lon_gw = None
        alt_gw = None
        for index, gw_dict in enumerate(metadata['gateways']):
            gw_defdic = defaultdict(lambda: None)
            gw_defdic.update(gw_dict)
            if index == 0:
                rssi = gw_defdic['rssi']
                lat_gw = gw_defdic['latitude']
                lon_gw = gw_defdic['longitude']
                alt_gw = gw_defdic['altitude']
            elif gw_defdic['latitude'] and gw_defdic['longitude']:
                if gw_defdic['rssi'] > rssi:
                    rssi = gw_defdic['rssi']
                    lat_gw = gw_defdic['latitude']
                    lon_gw = gw_defdic['longitude']
                    alt_gw = gw_defdic['altitude']
        return lat_gw, lon_gw, alt_gw, rssi


    def prepare_data(self, data):
        data_for_storing = {}
        keys = [
            'timestamp', 'pressure_pa', 'temp_c', 'core_temp_c', 'alt_m', 'bat_mv', 'lat',
            'lon', 'loop_time_s', 'lat_gw', 'lon_gw', 'alt_gw', 'freq', 'rssi'
            ]
        for key in keys:
            data_for_storing.setdefault(key, None)

        # timestamp
        data_for_storing['timestamp'] = data['timestamp']

        # data from GPS
        if data['payload_fields']:
            gps_data = data['payload_fields'].items()
            for key, value in gps_data:
                data_for_storing[key] = value
        # lat, lon & alt from gateways
        # either from metadata or from strongest rssi gateway
        if data['metadata']:
            metadata = defaultdict(lambda: None)
            metadata.update(data['metadata'])
            if metadata['gateways']:
                if self.identify_strongest_gw(metadata):
                    lat_gw, lon_gw, alt_gw, rssi = self.identify_strongest_gw(metadata)
            if metadata['latitude'] and metadata['longitude']:
                lat_gw = metadata['latitude']
                lon_gw = metadata['longitude']
                if metadata['altitude']:
                    alt_gw = metadata['altitude']
            try:
                data_for_storing['lat_gw'] = lat_gw
                data_for_storing['lon_gw'] = lon_gw
            except UnboundLocalError:
                pass
            try:
                data_for_storing['alt_gw'] = alt_gw
            except UnboundLocalError:
                pass
            try:
                data_for_storing['rssi'] = rssi
            except UnboundLocalError:
                pass
            if metadata['frequency']:
                data_for_storing['freq'] = metadata['frequency']
        # treat values of 0 as missing, values must be float / integer / json
        for key, value in data_for_storing.items():
            if value == 0 or type(value) == str:
                data_for_storing[key] = None
        self.store_data(data_for_storing, data)

    def store_data(self, data, json):
        self.__cursor.execute(f'''
            INSERT INTO data VALUES (
            "{data['timestamp']}",
            "{data['pressure_pa']}",
            "{data['temp_c']}",
            "{data['core_temp_c']}",
            "{data['alt_m']}",
            "{data['lat']}",
            "{data['lon']}",
            "{data['bat_mv']}",
            "{data['loop_time_s']}",
            "{data['lat_gw']}",
            "{data['lon_gw']}",
            "{data['alt_gw']}",
            "{data['freq']}",
            "{data['rssi']}",
            "{json}")''')
        self.__connection.commit()

    def fetch_all_data(self):
        data = self.__cursor.execute('SELECT * FROM data;').fetchall()
        self.__connection.commit()
        data_ls = []
        for line in data:
            data_ls.append(list(line))
        return data_ls

