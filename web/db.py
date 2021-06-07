import sqlite3


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
                gps_fix INTEGER,
                json TEXT)''')

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
            "{data['battery_mv']}",
            "{data['loop_time_s']}",
            "{data['gps_fix']}",
            "{data}")''')
        self.__connection.commit()

    def fetch_all_data(self):
        data = self.__cursor.execute('SELECT * FROM data;').fetchall()
        data_ls = []
        for line in data:
            data_ls.append(list(line))
        return data_ls

    def fetch_data_for_graph(self):
        data = self.__cursor.execute('''
            SELECT timestamp, temp_c, alt_m FROM data;''').fetchall()
        return data