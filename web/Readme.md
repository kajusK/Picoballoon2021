### app.py
* run flask application in current context
* endpoint() authorizes incoming data, adds timestamp, make defaultdic and send data to db.py for storing into database
* provide_data() fetches all data from database and handles invalid values, return data in pretty format (rounded, with suffixes)
* functions provide_data_table(), provide_data_markers(), provide_data_graphs() prepares data for markers, summary table and graphs, which are delivered using index() to index.html, for webuser to see

### db.py
* creates database and its structure if needed
* prepare_data() extracts all usefull data from received defaultdic, zero values and strings are treated as missing, sends data to store_data() for storing into sqlite3 database
* can also fetch all data from database (fetch_all_data())

### index.html
* uses bootstrap 5 for responsive website
* api.mapy.cz displays map with markers (and their cards) and balloon route
* scrollable summary table
* section about and picture of probe
* graphs with change of temperature and altitude

### /tests
* test_app() provides various tests to determine endpoint() and class Database works correctly

### Database structure in details:
* timestamp (int)
* freq (real) - communication frequency
* rssi (int) - received signal strength indication (in dbm)
* pressure_pa (integer) - air pressure (in pascal)
* temp_c (real) & core_temp_c - outside temperature and temperature of core (in C°)
* alt_m (int) - altitude (in metres)
* lat & lon (real) - latitude and longitude from GPS
* bat_mv (int) - battery voltage (in milivolts)
* loop_time_s (int) - processor time awake (in seconds)
* lat_gw (real) & lon_gw (real) - latitude and longitude from gateway
* alt_m (int) - altitude (in metres) from gateway
* json (text) - raw received data