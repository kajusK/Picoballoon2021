import sqlite3


class Database:

    def __init__(self):
        self.__connection = sqlite3.connect('database.sqlite')
        self.__cursor = self.__connection.cursor()

    def create_database_structure(self):
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                timestamp INTEGER,
                freq REAL,
                rssi INTEGER,
                estimated_lat REAL,
                estimated_lon REAL,
                pressure_pa INTEGER,
                temp_c REAL,
                core_temp_c REAL,
                alt_m INTEGER,
                lat REAL,
                lon REAL,
                battery_mv INTEGER,
                loop_time_s INTEGER,
                gps_fix INTEGER,
                json TEXT)''')

    def store_data(self, data):
        self.__cursor.execute(f'''
            INSERT INTO data VALUES (
            "{data['timestamp']}",
            "{data['freq']}",
            "{data['rssi']}",
            "{data['estimated_lat']}",
            "{data['estimated_lon']}",
            "{data['pressure_pa']}",
            "{data['temp_c']}",
            "{data['core_temp_c']}",
            "{data['alt_m']}",
            "{data['lat']}",
            "{data['lon']}",
            "{data['battery_mv']}",
            "{data['loop_time_s']}",
            "{data['gps_fix']}",
            "{data}")''')
        self.__connection.commit()