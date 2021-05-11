# To do list:
    # create sqlite database
    # store data from cloud in database
        # estimate longitude and latitude
    # display web content to user
        # add information points in map


import sqlite3


connection = sqlite3.connect('database.sqlite')
cursor = connection.cursor()


def create_database_structure():
    '''
    Database structure explained:
        timestamp (int)
        freq (real) - communication frequency
        rssi (int) - received signal strength indication (in dbm)
        estimated_lat (real) & estimated_lon (real) - estimated longitude and latitude (derived from gateway locations)
        pressure_pa (integer) - air pressure (in pascal)
        temp_c (real) & core_temp_c - outside temperature and temperature of core (in C°)
        alt_m (int) - altitude (in metres)
        lat & lon (real) - latitude and longitude from GPS
        battery_mv (int) - battery voltage (in milivolts)
        loop_time_s (int) - processor time awake (in seconds)
        gps_fix (int) - for (non)valid data from gps (1 - valid, 0 - nonvalid)
        json (text) - raw received data
    '''
    cursor.execute('''
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
            json TEXT
            )''')


create_database_structure()