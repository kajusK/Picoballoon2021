### Database structure in details:
* timestamp (int)
* freq (real) - communication frequency
* rssi (int) - received signal strength indication (in dbm)
* estimated_lat (real) & estimated_lon (real) - estimated longitude and latitude (derived from gateway locations)
* pressure_pa (integer) - air pressure (in pascal)
* temp_c (real) & core_temp_c - outside temperature and temperature of core (in C°)
* alt_m (int) - altitude (in metres)
* lat & lon (real) - latitude and longitude from GPS
* battery_mv (int) - battery voltage (in milivolts)
* loop_time_s (int) - processor time awake (in seconds)
* gps_fix (int) - for (non)valid data from gps (1 - valid, 0 - nonvalid)
* json (text) - raw received data
