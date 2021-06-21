import sqlite3
from collections import defaultdict

class Database:

    def __init__(self, path):
        self.__connection = sqlite3.connect(f'{path}/database.sqlite',  check_same_thread=False)
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
                battery_mv INTEGER,
                loop_time_s INTEGER,
                alt_gw INTEGER,
                lat_gw REAL,
                lon_gw REAL,
                json TEXT)''')

    def indentify_strongest_gw(self, metadata):
        '''
        Determine strongest RSSI from an array of gateways,
        return strongest gateway latitude, longitude and altitude
        if essential values are absent, return None
        '''
        try:
            for index, gateway in enumerate(metadata['gateways']):
                if gateway and index == 0:
                    strongest_gw = (gateway['rssi'], index)
                elif gateway and (gateway['rssi'] > strongest_gw[0]):
                    strongest_gw = (gateway['rssi'], index)
                gw_data = metadata['gateways'][strongest_gw[1]]
                lat_gw = gw_data['latitude']
                lon_gw = gw_data['longitude']
                if gw_data['altitude']:
                    alt_gw = gw_data['altitude']
                else:
                    alt_gw = None
                return lat_gw, lon_gw, alt_gw
        except KeyError:    # absent rssi / lat / lon
            return None

    def prepare_data(self, data):
        data_for_storing = {}
        keys = [
            'timestamp', 'alt_m', 'bat_mv', 'core_temp_c', 'lat',
            'lon', 'loop_time_s', 'pressure_pa', 'temp_c',
            'alt_gw', 'lat_gw', 'lon_gw'
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
                if self.indentify_strongest_gw(metadata):
                    lat_gw, lon_gw, alt_gw = self.indentify_strongest_gw(metadata)
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
        self.store_data(data_for_storing)

    def store_data(self, data):
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
            "{data}")''')
        self.__connection.commit()

    def fetch_all_data(self):
        data = self.__cursor.execute('SELECT * FROM data;').fetchall()
        data_ls = []
        for line in data:
            data_ls.append(list(line))
        return data_ls
